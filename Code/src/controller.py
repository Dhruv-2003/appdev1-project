## core functions for the app , like routes we want to use, and logic of the app
from flask import render_template, url_for, request, redirect, Flask
from app import app
from .models import User, Librarian, Book, Review, BookIssue, Section

@app.route('/')
def index():
    return render_template('index.html')

