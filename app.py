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

# Create the clients table to showcase information of each client
cursor.execute("""
CREATE TABLE IF NOT EXISTS clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    handle TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    cost NUMERIC,
    notes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id))
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
            
        except sqlite3.IntegrityError:
            flash("Username already taken")
            return redirect("/register")

    else:
        return render_template("register.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
    
        if not username:
            flash("Username is required")
            return redirect("/login")

        elif not password:
            flash("Password is required")
            return redirect("/login")
        
        # Create a new database connection and cursor for this request
        # Cannot use the global connection/cursor because of threading issues
        conn = sqlite3.connect("client.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            flash("Incorrect information")
            return redirect("/login")
        
        check_password = row[1]

        # check_password_hash returns True or False
        # No need to check if username == check_username because I already passed the username form into the query
        if check_password_hash(check_password, password):

            # No need to "if row:" and "else: user_id = None" because I already checked if row exist above
            user_id = row[0]

            # Store id of the user from users table in session
            session["user_id"] = user_id

            return redirect("/")
        
        else:
            flash("Incorrect information")
            return redirect("/login")

    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
@login_required
def index():
    # Create a new database connection and cursor for this request
    # Cannot use the global connection/cursor because of threading issues
    conn = sqlite3.connect("client.db")
    cursor = conn.cursor()
        
    cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
    row = cursor.fetchone()
    username = row[0]

    cursor.execute("SELECT handle, platform, status, cost, notes, id FROM clients WHERE user_id = ?", (session["user_id"],))
    table = cursor.fetchall()
    conn.close()

    return render_template("index.html", username=username, table=table)

# re is a module to work with regular expressions (patterns for matching text)
import re

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        link = request.form.get("link")
        if not link:
            flash("Profile link required")
            return redirect("/add")
        
        # Proceed if the link is from the platforms' list
        platforms = ["youtube", "instagram", "tiktok"]
        found = False
        for p in platforms:
            if p in link.lower():
                found = True
                platform = p.capitalize()
                break
        if not found:
            flash("Link must come from YouTube, Instagram, TikTok")
            return redirect("/add")

        # In regex . by itself means any single character so we type \. to call for a .
        # ([^/]+) captures everything up until the next /
        # @? matches either an @ or nothing
        # re.search returns a match object so capturing the text, you need .group(1)
        # .group(0) returns the full regex match (no brackets) and .group(1) returns the text that matched the first group (first bracket: ([^/]+))
        match = re.search(r"\.com/@?([^/]+)", link)

        if not match:
            flash("Could not find handle")
            return redirect("/add")

        handle = match.group(1)
        status = "Lead"
        cost = ""
        notes = ""
        
        # Create a new database connection and cursor for this request
        # Cannot use the global connection/cursor because of threading issues
        conn = sqlite3.connect("client.db")
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO clients (user_id, handle, platform, status, cost, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], handle, platform, status, cost, notes)
        )
        conn.commit()
        conn.close()

        return redirect("/")
    
    else:
        return render_template("add.html")
    
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    if request.method == "POST":
        back = request.form.get("back")
        save = request.form.get("save")

        handle = request.form.get("handle")
        platform = request.form.get("platform")
        status = request.form.get("status")
        cost = request.form.get("cost")
        notes = request.form.get("notes")

        if back:
            return redirect("/")
        
        if save:
            # Create a new database connection and cursor for this request
            # Cannot use the global connection/cursor because of threading issues
            conn = sqlite3.connect("client.db")
            cursor = conn.cursor()

            cursor.execute("UPDATE clients SET handle=?, platform=?, status=?, cost=?, notes=? WHERE id = ?", (handle, platform, status, cost, notes, id))
            conn.commit()
            conn.close()

            flash("Updated client information")
            return redirect("/")
        
        flash("Unable to save")
        return redirect("/")
    
    else:
        # Create a new database connection and cursor for this request
        # Cannot use the global connection/cursor because of threading issues
        conn = sqlite3.connect("client.db")
        cursor = conn.cursor()

        cursor.execute("SELECT handle, platform, status, cost, notes, id FROM clients WHERE id = ?", (id,))
        table = cursor.fetchall()
        conn.close()

        return render_template("edit.html", table=table)