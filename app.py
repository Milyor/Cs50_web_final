import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("recommender.html")

if __name__ == '__main__':
    app.run(debug=True)