# Did not include import os
# Using sqlite3 instead of from cs50 import SQL
import sqlite3

# Only using from flask import session
# from flask_session import Session is not needed for a small project
from flask import Flask, flash, redirect, render_template, request, session

# This is to add wraps into my decorator so the replaced function name stays the same
from functools import wraps

# Configure application
app = Flask(__name__)

# Make a new db
conn = sqlite3.connect("client.db")
cursor = conn.cursor()

# Create the user table
cursor.execute("""
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL)
""")

# Save all changes
conn.commit()

# Close once at the end
conn.close()

# The after_request will clear the cache which is important to not save users' sensitive data
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Decorate routes to require login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# All the routes
@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    return render_template("add.html")