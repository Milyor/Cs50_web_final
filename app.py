from dotenv import load_dotenv 
import os
from igdb.wrapper import IGDBWrapper
from flask import Flask, flash, redirect, render_template, request, session
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
                           
except FileNotFoundError:
    pass

@app.route("/", methods=["GET", "POST"])
def home():
    global cached_indie_games
    
    genres = []
    similar_games = []
    error_message = None 
    if request.method == "POST":
        game_name = request.form.get("game")
        if not game_name:
            error_message_game = "Please fill out the game field. "
            return render_template("recommender.html", error_message_game=error_message_game)     
        try: 
            #search for the game
            response = wrapper.api_request(
                'games',
                f'search "{game_name}"; fields name, id; limit 1;'
            )
            decoded_data = json.loads(response.decode('utf-8'))
            
            # Check if any games were found
            if not decoded_data:
                error_message_game = f"No game found with the name '{game_name}'."
                return render_template("recommender.html", error_message_game=error_message_game)
            
            
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
            all_games_response = None
            
            if not cached_indie_games:
                all_games_response = wrapper.api_request(
                    'games',
                    f'fields name, id, genres.name; where genres.name = "Indie"; limit 200;'
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
            
            # Checking for similar games  
            excluded_genre = 'Indie'
            
            for indie_game in cached_indie_games:
                similarity_score = calculate_similarity(genres, indie_game['genres'], excluded_genre)
                similar_games.append({'name': indie_game['name'], 'similarity': similarity_score, 'id': indie_game['id']})
                
            similar_games = sorted(similar_games, key=lambda x: x['similarity'], reverse=True)
            
            # Top games
            top_similar_games = []
            for indie_game in similar_games[:5]:
                game_data = {'name': indie_game['name'], 'similarity': indie_game['similarity']}
                
                # Check if 'id' key is present in the dictionary
                if 'id' in indie_game:
                    game_data['id'] = indie_game['id']
                else:
                    game_data['id'] = None
                top_similar_games.append(game_data)
                                
            # Fetching 1080p cover image URLs for top similar games
            cover_urls = []
            summaries = []
            
            for game in top_similar_games:
                game_id = game['id']
                if game_id:
                    game_details_response = wrapper.api_request(
                        'games',
                        f'fields name, cover.url, summary; where id = {game_id};'
                    )
                    
                    games_details = json.loads(game_details_response.decode('utf-8'))
                    
                    if games_details:
                        cover_url = games_details[0].get('cover',{}).get('url')
                        if cover_url:
                            # Appending 't_1080p" to the end to get the 1080p image
                            cover_urls.append(f"https://images.igdb.com/igdb/image/upload/t_1080p/{cover_url.split('/')[-1]}")
                        summary = games_details[0].get('summary')
                        summaries.append(summary if summary else "no summary available") 
                                
            return render_template("recommender.html", decoded_data=decoded_data, game_id=game_id, error_message = error_message, top_similar_games = top_similar_games, cover_urls=cover_urls, summaries=summaries)
    
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
    