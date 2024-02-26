from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from src.database import db


app = Flask(__name__, template_folder='templates')
# relative path for the location of the db

import config
import src.controller
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)
app.app_context().push()

if __name__  == '__main__':
    app.run(debug=True)