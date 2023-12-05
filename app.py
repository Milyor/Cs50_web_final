from dotenv import load_dotenv 
import os
from cs50 import SQL
from igdb.wrapper import IGDBWrapper
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re
import json

load_dotenv()
api_key = os.getenv("API_TOKEN")
api_user_key = os.getenv("API_USER_KEY")
wrapper = IGDBWrapper(api_user_key, api_key)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        game_name = request.form.get("game")
        byte_array = wrapper.api_request(
            'games',
            f'search "{game_name}"; fields id, name, release_dates.human; limit 5;'
        )
        
        decoded_data = json.loads(byte_array.decode('utf-8'))
        
        game_names = [item['name'] for item in decoded_data]
        
        return render_template("recommender.html",game_names=game_names)
    
    return render_template("recommender.html")


if __name__ == '__main__':
    app.run(debug=True)