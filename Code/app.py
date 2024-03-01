import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from src.database import db

app = None

def create_app():
    app = Flask(__name__, template_folder='templates')
    # relative path for the location of the db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.secret_key = os.getenv('SECRET_KEY')     
    db.init_app(app)
    app.app_context().push()
    login_manager = LoginManager()
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()
    return app

app = create_app()

import config
import src.controller

if __name__  == '__main__':
    app.run(debug=True)