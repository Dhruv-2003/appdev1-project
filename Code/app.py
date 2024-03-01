from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
# import os
# from python_dotenv import load_dotenv
from src.database import db
# load_dotenv()

app = Flask(__name__, template_folder='templates')
# relative path for the location of the db

import config
# from src.controller import login_manager
import src.controller
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
# app.secret_key = os.getenv('SECRET_KEY') 

db.init_app(app)
# login_manager.init_app(app)
app.app_context().push()

# with app.app_context():
#     db.create_all()

if __name__  == '__main__':
    app.run(debug=True)