# Did not include import os
# Using sqlite3 instead of from cs50 import SQL
import sqlite3

# Only using from flask import session
# from flask_session import Session is not needed for a small project
from flask import Flask, flash, redirect, render_template, request, session
