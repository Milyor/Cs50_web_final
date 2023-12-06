from dotenv import load_dotenv 
import os
from cs50 import SQL
from igdb.wrapper import IGDBWrapper
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from werkzeug.security import check_password_hash, generate_password_hash
import re
import json
import pandas as pd
import numpy as np

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
                
                genres_response = wrapper.api_request(
                    'games',
                    f'fields genres.name; where id = {game_id}; limit 5;'
                )
                genres_data = json.loads(genres_response.decode('utf-8'))
                if genres_data and 'genres' in genres_data[0]:
                    genres = genres_data[0]['genres']
                
                return render_template("recommender.html", decoded_data=decoded_data, game_id=game_id, genres = genres)
            
            else:
                
                flash(f"No results found for the game: {game_name}")
                
        except Exception as e:
        # Handle API request errors
            flash(f"Error: {str(e)}")
        
    return render_template("recommender.html")


if __name__ == '__main__':
    app.run(debug=True)