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

cached_data_file = "games_list.json"

cached_indie_games = []
# Load cached data from the file if its exists
try:
    with open(cached_data_file, "r") as file:
        file_contents = file.read()
        if file_contents:
            cached_data = json.loads(file_contents)
            if isinstance(cached_data, list):
                cached_indie_games = cached_data
         
                game_ids_by_name = {}
            
except FileNotFoundError:
    pass

@app.route("/", methods=["GET", "POST"])
def home():
    global cached_indie_games
    global game_ids_by_name
    cover_urls = []
    genres = []
    similar_games = []
    error_message = None 
    if request.method == "POST":
        game_name = request.form.get("game")
        if not game_name:
            flash("Fill out the field with a game")
            return render_template("recommender.html")
        all_games_response = None
        
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
                if not cached_indie_games:
                    all_games_response = wrapper.api_request(
                        'games',
                        f'fields name, id, genres.name; where genres.name = "Indie"; limit 100;'
                    )
                
                    all_games_data = json.loads(all_games_response.decode('utf-8'))
                        
                        # Initialized an empty list to store indie games
                    if all_games_data:
                            cached_indie_games = [{'name': game['name'], 'genres': game['genres'], 'id': game['id']} for game in all_games_data]                           
                            game_ids_by_name = {game['name']: game['id'] for game in cached_indie_games}
                            with open(cached_data_file, "w") as file:
                                json.dump(cached_indie_games, file)
                    else:
                         error_message = "No indie games found" 
                
                # checking for similar games  
                excluded_genre = 'Indie'
                
                for indie_game in cached_indie_games:
                    similarity_score = calculate_similarity(genres, indie_game['genres'], excluded_genre)
                    similar_games.append({'name': indie_game['name'], 'similarity': similarity_score})
                    
                similar_games = sorted(similar_games, key=lambda x: x['similarity'], reverse=True)
                
                #Top games
                top_similar_games = [{'name': indie_game['name'], 'similarity': indie_game['similarity']} for indie_game in similar_games[:5]]
  
                
                # Fetching 1080p cover image URLs for top similar games
                for game in top_similar_games:
                    game_name = game['name']
                    if game_name in game_ids_by_name:
                        game_id = game_ids_by_name[game_name]
                    if game_id:
                        
                        game_details_response = wrapper.api_request(
                            'games',
                            f'fields name, cover.url; where id = {game_id};'
                        )
                        
                        games_urls = json.loads(game_details_response.decode('utf-8'))
                        
                        if games_urls and games_urls[0].get('cover'):
                            cover_url = games_urls[0]['cover']['url']
                            # Appending 't_1080p" to the end to get the 1080p image
                            cover_urls.append(f"https://images.igdb.com/igdb/image/upload/t_1080p/{cover_url.split('/')[-1]}")
                                 
                return render_template("recommender.html", decoded_data=decoded_data, game_id=game_id, error_message = error_message, top_similar_games = top_similar_games, cover_urls=cover_urls)
            
            else:
                
                flash(f"No results found for the game: {game_name}")
                
        except Exception as e:
        # Handle API request errors
            flash(f"Error: {str(e)}")
        
    return render_template("recommender.html")

# Calculate the similarity of the genres
def calculate_similarity(genres1, genres2, excluded_genre):
    set1 = set(genre['name'] for genre in genres1) - {excluded_genre}
    set2 = set(genre['name'] for genre in genres2) - {excluded_genre}
    
    # calculate Jaccard similarity
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    # add a boost to similarity if the additional genre is present
    similarity = len(intersection) / len(union) + 0.2 if len(union) > 0 else 0
    
    return similarity
    
@app.route("/test")
def test():
    return "This is a test route"

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)