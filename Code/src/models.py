from .database import db
from datetime import datetime
from flask_login import UserMixin

from app import app

# from app import app

## All the models for the app
# like User , Books , etc

## LIBRARIAN 
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# NAME VARCHAR(100) NOT NULL
# USERNAME/EMAIL VARCHAR(100) NOT NULL
# PASSWORD VARCHAR(100) NOT NULL ## Hashed
# * Sections RELATIONSHIP to SECTION
# * Books RELATIONSHIP to BOOK
# * Books Issues RELATIONSHIP to BOOK_ISSUE
class Librarian(db.Model, UserMixin):
    __tablename__ = 'librarian'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    active = db.Column(db.Boolean)
    role = 'librarian'
    
    ## relationship - one to many
    sections = db.relationship('Section', backref='librarian', lazy=True)
    books = db.relationship('Book', backref='librarian', lazy=True)
    books_issues = db.relationship('BookIssue', backref='librarian', lazy=True)

## USER
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# NAME VARCHAR(100) NOT NULL
# USERNAME/EMAIL VARCHAR(100) NOT NULL
# PASSWORD VARCHAR(100) NOT NULL ## Hashed
# * BooksBorrowed RELATIONSHIP to BOOK_ISSUE
# TotalBooksBorrowed INT NOT NULL
class User(db.Model , UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    total_books_borrowed = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean)
    role = 'user'
    
    ## relationship - one to many
    books_borrowed = db.relationship('BookIssue', backref='user', lazy=True)

## SECTION
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# Librarian ID  NOT NULL FOREIGN KEY
# Name VARCHAR(100) NOT NULL
# Date_created DATETIME NOT NULL
# Description VARCHAR(100) NOT NULL
# * Books RELATIONSHIP to BOOK
class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default= datetime.now())
    description = db.Column(db.String(100), nullable=False)
    
    ## relationship - one to many
    books = db.relationship('Book', backref='section', lazy=True)

## BOOK
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# Name VARCHAR(100) NOT NULL
# Content VARCHAR(100) NOT NULL *** issue regarding format ***
# Author(s) VARCHAR(100) NOT NULL
# Section ID * FOREIGN KEY
# Librarian ID * FOREIGN KEY
# NoPages INT NOT NULL
# Date_created DATETIME NOT NULL
# Description VARCHAR(100) NOT NULL
# Rating INT NOT NULL
# * Reviews RELATIONSHIP to REVIEW
# Cover *** issue
# PDF *** issue
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    content = db.Column(db.String(512), nullable=False)
    authors = db.Column(db.String(32), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)
    no_of_pages = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, nullable=False, default= datetime.now())
    description = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    
    ## relationship - one to many
    reviews = db.relationship('Review', backref='book', lazy=True)
    issues =  db.relationship('BookIssue', backref='book', lazy=True)

## REVIEW
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# Book ID FOREIGN KEY
# User ID FOREIGN KEY
# Content VARCHAR(100) NOT NULL
class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(100), nullable=False)

## BOOK_ISSUE
# ID PRIMARY KEY , UNIQUE, AUTOINCREMENT, NOT NULL
# Book ID FOREIGN KEY 
# User ID FOREIGN KEY
# Librarian ID FOREIGN KEY
# Date requested DATETIME NOT NULL
# Date issued DATETIME 
# Return date DATETIME 
# Status ENUM('REQUESTED','REJECTED','ISSUED','RETURNED','REVOKED') NOT NULL  // Status Revoked automatically if the return date is passed
class BookIssue(db.Model):
    __tablename__ = 'book_issue'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)
    date_requested = db.Column(db.DateTime, nullable=False, default= datetime.now())
    date_issued = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.Enum('REQUESTED','REJECTED','ISSUED','RETURNED','REVOKED'), nullable=False)

with app.app_context():
    db.create_all()