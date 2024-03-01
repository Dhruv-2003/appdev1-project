## core functions for the app , like routes we want to use, and logic of the app
from flask import render_template, url_for, request, redirect, Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import bcrypt
from app import app
from .database import db
from .models import User, Librarian, Book, Review, BookIssue, Section 
from datetime import datetime, timedelta

## MAIN PAGE ROUTES
login_manager = LoginManager()

def librarian_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if the current user is a librarian
        if not current_user.role == 'librarian':
            return redirect(url_for('unauthorized'))
        return func(*args, **kwargs)
    return decorated_function

## Home page
@app.route('/')
def index():
    # fetch all the books directly for all the sections
    return render_template('index.html')

### LIBRARIAN ROUTES

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
            login_user(librarian)
            return redirect(url_for('/librarian/dashboard'))
        except:
            return 'There was an issue adding the librarian'
    else:
        return render_template('librarian/register.html')

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
                login_user(librarian)
                return redirect(url_for('/librarian/dashboard'))
            else:
                return 'Invalid Password'
        else:
            return 'Invalid Username'
    else:
        return render_template('librarian/login.html')
    
## Librarian add book
@app.route('/librarian/add_book', methods=['POST', 'GET'])
@login_required
@librarian_required
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
        return render_template('librarian/add_book.html')

## Librarian edit book
@app.route('/librarian/edit_book/<int:id>', methods=['POST', 'GET'])
@login_required
@librarian_required
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
        return render_template('librarian/edit_book.html', book=book)

## Librarian add section
@app.route('/librarian/add_section', methods=['POST', 'GET'])
@login_required
@librarian_required
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
        return render_template('librarian/add_section.html')

## Librarian dashboard
@app.route('/librarian/dashboard')
@login_required
@librarian_required
def librarian_dashboard():
    return render_template('librarian/dashboard.html')

### USER ROUTES

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
        return render_template('user/register.html')

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
        return render_template('user/login.html')
    

## User dashboard
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user/dashboard.html')

### BOOK ROUTES

## Get book , also them to request books
@app.route('/book/<int:id>', methods=['POST', 'GET'])
@login_required
def book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        librarian_id = request.form['librarian_id']
        status = "REQUESTED"
        ## MIGHT NEED TO CHECK THE USER'S BOOKS BORROWED
         ## MIGHT NEED TO ADD THE BOOKS TO THE USER'S BOOKS BORROWED
        user = User.query.get_or_404(book_issue.user_id)
        total_books_borrowed = user.total_books_borrowed
        if total_books_borrowed <5:
            book_issue = BookIssue(user_id=user_id, book_id=book_id, librarian_id=librarian_id, status=status)
            try:
                db.session.add(book_issue)
                db.session.commit()
                return redirect(url_for('/book/<id>'))
            except:
                return 'There was an issue adding the book'
        else:        
            return 'You have reached the maximum limit of books borrowed'
        
    else:
        return render_template('book.html', book=book)

## View Book
@app.route('/user/view_book/<int:id>', methods=['POST', 'GET'])
@login_required
# Check if user does own this book
def view_book(id):
    book = Book.query.get_or_404(id)
    ## Check if the book is indeed issued to the user
    ## If yes, then render the view_book.html
    ## Else, redirect to the book page
    return render_template('book/view.html', book=book)

## Read book
@app.route('/user/read_book/<int:id>', methods=['POST', 'GET'])
@login_required
# Check if user does own this book
def read_book(id):
    book = Book.query.get_or_404(id)
    ## Check if the book is indeed issued to the user
    ## If yes, then render the view_book.html
    ## Else, redirect to the book page
    return render_template('book/read.html', book=book)


## POST ONLY ROUTE

## Review book
@app.route('/user/review_book/<int:id>', methods=['POST'])
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

## Issue book
@app.route('/librarian/issue_book/<int:id>', methods=['POST'])
@login_required
@librarian_required
def issue_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page

        user = User.query.get_or_404(book_issue.user_id)
        total_books_borrowed = user.total_books_borrowed
        if total_books_borrowed >= 5:
            book_issue.status = "REJECTED"
            return 'User has reached the maximum limit of books borrowed'
        
        book_issue.status = "ISSUED"
        book_issue.date_issued = datetime.utcnow()
        book_issue.return_date = datetime.utcnow() + timedelta(days=7)

        ## MIGHT NEED TO ADD THE BOOKS TO THE USER'S BOOKS BORROWED
        user.total_books_borrowed += 1

        try:
            db.session.commit()
        except:
            return 'There was an issue issuing the book'

## Reject book
        
@app.route('/librarian/reject_book/<int:id>', methods=['POST'])
@login_required
@librarian_required
def reject_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page
        book_issue.status = "REJECTED"
        try:
            db.session.commit()
        except:
            return 'There was an issue rejecting the book request'
        
          
## Return book
@app.route('/librarian/return_book/<int:id>', methods=['POST'])
@login_required
@librarian_required
def return_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page

        current_date = datetime.utcnow()

        if current_date > book_issue.return_date:
            book_issue.status = "REVOKED"
            return 'Return date passed, book revoked'
       
        book_issue.status = "RETURNED"
       
        try:
            db.session.commit()
        except:
            return 'There was an issue issuing the book'
       
## Revoke book
@app.route('/librarian/revoke_book/<int:id>', methods=['POST'])
@login_required
@librarian_required
def revoke_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page

        current_date = datetime.utcnow()

        if current_date < book_issue.return_date:
            return 'Return date not yet passed , cannot revoke the book'
       
        book_issue.status = "REVOKED"
       
        try:
            db.session.commit()
        except:
            return 'There was an issue issuing the book'

## Remove Book 
@app.route('/librarian/remove_book/<int:id>', methods=['POST']) 
@login_required
@librarian_required
def remove_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(book)
            db.session.commit()
        except:
            return 'There was an issue removing the book'       

## Remove Section
@app.route('/librarian/remove_section/<int:id>', methods=['POST'])
@login_required
@librarian_required
# Check if these section is valid
def remove_section(id):
    section = Section.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(section)
            db.session.commit()
        except:
            return 'There was an issue removing the section'

### GET ONLY ROUTES
    
## Search book by name
@app.route('/search_book_by_name', methods=['GET'])
def search_book_by_name():
    name = request.form['name']
    books = Book.query.filter_by(Book.name.like(f"%{name}%")).all()
    return render_template('index.html', books=books)
        
## Search book by author
@app.route('/search_book_by_author', methods=['GET'])
def search_book_by_author():
    author = request.form['author']
    books = Book.query.filter_by(Book.authors.like(f"%{author}%")).all()
    return render_template('index.html', books=books)
        

## Get book for a section
@app.route('/get_section_books/<string:section>', methods=['GET'])
def get_section_books(section):
    section = Section.query.filter_by(name=section).first()
    books = section.books
    return render_template('index.html', books=books)