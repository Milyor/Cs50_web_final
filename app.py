from dotenv import load_dotenv 
import os
from cs50 import SQL
from igdb.wrapper import IGDBWrapper
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re
import json

# Credentials
load_dotenv()
api_key = os.getenv("API_TOKEN")
api_user_key = os.getenv("API_USER_KEY")
wrapper = IGDBWrapper(api_user_key, api_key)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    genres = []
    if request.method == "POST":
        game_name = request.form.get("game")
        if not game_name:
            flash("Fill out the field with a game")
            return render_template("recommender.html")
        
        try: 
            #search for the game
            response = wrapper.api_request(
                'games',
                f'search "{game_name}"; fields name, id; limit 1;'
            )
            decoded_data = json.loads(response.decode('utf-8'))
            
            #check if any games were found
            if decoded_data:
                game_id = decoded_data[0]['id']
                
                # Fetch genres for the input game
                genres_response = wrapper.api_request(
                    'games',
                    f'fields genres.name; where id = {game_id}; limit 5;'
                )
                genres_data = json.loads(genres_response.decode('utf-8'))
                if genres_data and 'genres' in genres_data[0]:
                    genres = genres_data[0]['genres']
                 
                # Retrieving games where genres is indie, to not look for all the games if im just recommending indie games
                all_games_response = wrapper.api_request(
                    'games',
                    f'fields id, genres.name; where genres.name = "indie"; limit 50;'
                )
                
                all_games_data = json.loads(all_games_response.decode('utf-8'))
                
                # Initialized an empty list to store indie games
                filtered_games = []
                
                # Loop through each game 
                for game_data in all_games_data:
                    game_id = game_data['id']
                    
                    # extract the list of genres for the current game 
                    game_genres = game_data.get('genres', [])
                    
                    # storing the game details including genres in the filtered_games
                    filtered_games.append({'id': game_id, 'name': game_data['name'], 'genres': game_genres})
                if not filtered_games:
                    flash("No indie games found.")
                    return render_template("recommender.html")
                
                additional_genre = 'indie'
                
                similar_games = []
                
                for other_game in filtered_games:
                    other_game_id = other_game['id']
                    other_genres = other_game['genres']
                    similarity_score = calculate_similarity(genres, other_genres, additional_genre)
                    similar_games.append({'id': other_game_id, 'similarity': similarity_score})
                    
                similar_games = sorted(similar_games, key=lambda x: x['similarity'], reverse=True)
                
                # Get top N similar games
                
                top_n_similar_games = similar_games[:5]
                
                # Fetch additional information for the recommended games
                recommended_games_info = []
                
                for game in top_n_similar_games:
                    game_id = game['id']
                    response = wrapper.api_request(
                        'games',
                        f'fields name, summary, genres.name; where id = {game_id}; limit 1:'
                    )
                    recommended_games_info = json.loads(response.decode('utf-8'))
                    recommended_games_info.append(recommended_games_info)
                    
                recommended_game_names = [game_info[0]['name'] for game_info in recommended_games_info]
                
                return render_template("recommender.html", decoded_data=decoded_data, game_id=game_id, genres = genres, filtered_games = filtered_games)
            
            else:
                
                flash(f"No results found for the game: {game_name}")
                
        except Exception as e:
        # Handle API request errors
            flash(f"Error: {str(e)}")
        
    return render_template("recommender.html")


if __name__ == '__main__':
    app.run(debug=True)
    
# Calculate the similarity of the genres
def calculate_similarity(genres1, genres2, additional_genre):
    set1 = set(genres1)
    set2 = set(genres2)
    
    additional_genre_preset = additional_genre in set2 and additional_genre not in set1
    
    # calculate Jaccard similarity
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    # add a boost to similarity if the additional genre is present
    similarity = len(intersection) / len(union) + 0.2 if len(union) > 0 else 0
    
    #increase similarity if the additional genre is present 
    similarity += 0.3 if additional_genre_preset else 0
    return similarity
    