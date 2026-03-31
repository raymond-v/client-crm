# Did not include import os
# Using sqlite3 instead of from cs50 import SQL
import sqlite3

# Only using from flask import session
# from flask_session import Session is not needed for a small project
from flask import Flask, flash, redirect, render_template, request, session

# Tool for hashing passwords securely
from werkzeug.security import generate_password_hash, check_password_hash 

# This is to add wraps into my decorator so the replaced function name stays the same
from functools import wraps

# Configure application
app = Flask(__name__)

# Required for flash/session
app.secret_key = "supersecretkey"

# Make a new db
conn = sqlite3.connect("client.db")
cursor = conn.cursor()

# Create the user table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL)
""")

# Save all changes
conn.commit()

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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Name is required")
            return render_template("register.html")
        elif not password:
            flash("Password is required")
            return render_template("register.html")
        elif not confirmation:
            flash("Confirmation is required")
            return render_template("register.html")
        
        if password != confirmation:
            flash("Confirmation does not match password")
            return render_template("register.html")
        
        try:
            # Create a new database connection and cursor for this request
            # Cannot use the global connection/cursor because of threading issues
            conn = sqlite3.connect("client.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, generate_password_hash(password)))
            conn.commit()

            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                user_id = row[0]
            else:
                user_id = None

            # Store id of the user from users table in session
            session["user_id"] = user_id

            flash("Registration successful")
            return redirect("/")
            
        except ValueError:
            flash("Username already taken")
            return redirect("/register")

    else:
        return render_template("register.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    return render_template("add.html")