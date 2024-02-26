## core functions for the app , like routes we want to use, and logic of the app
from flask import render_template, url_for, request, redirect, Flask
import bcrypt
from app import app
from .database import db
from .models import User, Librarian, Book, Review, BookIssue, Section

## MAIN PAGE ROUTES

## Home page
@app.route('/')
def index():
    return render_template('index.html')

## Librarian registeration
@app.route('/librarian/register', methods=['POST', 'GET'])
def librarian_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        librarian = Librarian(username=username, password=hashed_password)
        try:
            db.session.add(librarian)
            db.session.commit()
            return redirect(url_for('/librarian/dashboard'))
        except:
            return 'There was an issue adding the librarian'
    else:
        return render_template('librarian_register.html')

## Librarian login
@app.route('/librarian/login', methods=['POST', 'GET'])
def librarian_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        librarian = Librarian.query.filter_by(username=username).first()
        if librarian:
            # if librarian.password == password:
            #     return redirect(url_for('librarian_dashboard'))
            if bcrypt.checkpw(password, librarian.password):
                return redirect(url_for('/librarian/dashboard'))
            else:
                return 'Invalid Password'
        else:
            return 'Invalid Username'
    else:
        return render_template('librarian_login.html')
    
## Librarian add book
@app.route('/librarian/add_book', methods=['POST', 'GET'])
def librarian_add_book():
    if request.method == 'POST':
        name = request.form['name']
        author = request.form['author']
        content = request.form['content']
        section_id = request.form['section_id']
        librarian_id = request.form['librarian_id']
        no_of_pages = request.form['no_of_pages']
        description = request.form['description']
        rating = 0
        book = Book(name=name, author=author,content=content, section_id=section_id, librarian_id=librarian_id, no_of_pages=no_of_pages, description=description, rating=rating)
        try:
            db.session.add(book)
            db.session.commit()
            return redirect(url_for('/librarian/dashboard'))
        except:
            return 'There was an issue adding the book'
    else:
        return render_template('librarian_add_book.html')

## Librarian edit book
@app.route('/librarian/edit_book/<int:id>', methods=['POST', 'GET'])
def librarian_edit_book():
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.name = request.form['name']
        book.author = request.form['author']
        book.content = request.form['content']
        book.section_id = request.form['section_id']
        book.no_of_pages = request.form['no_of_pages']
        book.description = request.form['description']
        
        try:
            db.session.commit()
            return redirect(url_for('/librarian/dashboard'))
        except:
            return 'There was an issue editing the book'
    else:
        return render_template('librarian_edit_book.html', book=book)

## Librarian add section
@app.route('/librarian/add_section', methods=['POST', 'GET'])
def librarian_add_section():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        librarian_id = request.form['librarian_id']
        section = Section(name=name, description=description, librarian_id=librarian_id)
        try:
            db.session.add(section)
            db.session.commit()
            return redirect(url_for('/librarian/dashboard'))
        except:
            return 'There was an issue adding the section'
    else:
        return render_template('librarian_add_section.html')

## Librarian dashboard
@app.route('/librarian/dashboard')
def librarian_dashboard():
    return render_template('librarian_dashboard.html')

## User registeration
@app.route('/user/register', methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('/user/dashboard'))
        except:
            return 'There was an issue adding the user'
    else:
        return render_template('user_register.html')

## User login
@app.route('/user/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.checkpw(password, user.password):
                return redirect(url_for('/user/dashboard'))
            else:
                return 'Invalid Password'
        else:
            return 'Invalid Username'
    else:
        return render_template('user_login.html')
    

## User dashboard
@app.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

## 

## Get book
@app.route('/book/<int:id>', methods=['POST', 'GET'])
def book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        librarian_id = request.form['librarian_id']
        status = "ISSUED"
        book_issue = BookIssue(user_id=user_id, book_id=book_id, librarian_id=librarian_id, status=status)
        try:
            db.session.add(book_issue)
            db.session.commit()
            return redirect(url_for('/book/<id>'))
        except:
            return 'There was an issue adding the book'
    else:
        return render_template('book.html', book=book)

## View Book
@app.route('user/view_book/<int:id>', methods=['POST', 'GET'])
def view_book(id):
    book = Book.query.get_or_404(id)
    ## Check if the book is indeed issued to the user
    ## If yes, then render the view_book.html
    ## Else, redirect to the book page
    return render_template('view_book.html', book=book)

## Read book
@app.route('user/read_book/<int:id>', methods=['POST', 'GET'])
def read_book(id):
    book = Book.query.get_or_404(id)
    ## Check if the book is indeed issued to the user
    ## If yes, then render the view_book.html
    ## Else, redirect to the book page
    return render_template('read_book.html', book=book)


## POST ONLY ROUTE

## Review book
@app.route('user/review_book/<int:id>', methods=['POST'])
def review_book(id):
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page
        user_id = request.form['user_id']
        book_id = id
        content = request.form['content']
        review = Review(user_id=user_id, book_id=book_id, content=content)
        try:
            db.session.add(review)
            db.session.commit()
        except:
            return 'There was an issue adding the review'
