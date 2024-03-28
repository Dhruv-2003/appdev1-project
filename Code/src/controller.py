## core functions for the app , like routes we want to use, and logic of the app
from flask import render_template, url_for, request, redirect, Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import bcrypt
from app import app
from .database import db
from .models import User, Librarian, Book, Review, BookIssue, Section 
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

# login_manager = LoginManager()


# @login_manager.user_loader
def load_user(user_id):
    print("User ID",user_id)
    user = User.query.get(int(user_id))
    if user:
        return user
    else:
        librarian = Librarian.query.get(user_id)
        if librarian:
            return librarian
        else:
            return None

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def librarian_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check if the current user is a librarian
        if not current_user.role == 'librarian':
            return redirect(url_for('unauthorized'))
        return func(*args, **kwargs)
    return decorated_function

## MAIN PAGE ROUTES

## Home page
@app.route('/')
def index():
    books = Book.query.all()
    available_books = []
    for book in books:
        if book.issue:
            ## TODO: Possibly change this to Available check in the new db
            if book.issue.status != 'ISSUED':
                available_books.append(book)
        else:
            available_books.append(book)

    sections = Section.query.all()
    # fetch all the books directly for all the sections
    return render_template('index.html', books= available_books,sections = sections)

### LIBRARIAN ROUTES

## Librarian registeration
@app.route('/librarian/register', methods=['POST', 'GET'])
def librarian_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        librarian = Librarian(username=username, password=hashed_password, name = name)
        try:
            db.session.add(librarian)
            db.session.commit()
            # login_user(librarian)
            return redirect(url_for('librarian_dashboard'))
        except Exception as error:
            print("An exception occurred:", error) # An exception occurred: 
            return str(error)
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
            if bcrypt.checkpw(password.encode('utf-8'), librarian.password):
                # login_user(librarian)
                return redirect(url_for('librarian_dashboard'))
            else:
                return 'Invalid Password'
        else:
            return 'Invalid Username'
    else:
        return render_template('librarian_dashboard')
    
## Librarian add book
@app.route('/librarian/add_book', methods=['POST', 'GET'])
# @login_required
# @librarian_required
def librarian_add_book():
    if request.method == 'POST':
        name = request.form['name']
        author = request.form['author']
        content = request.form['content']
        section_id = request.form['selected_section']
        cover_image = request.files['bookpdf']

        ## TODO: get librarian from record
        # librarian_id = request.form['librarian_id']
        librarian_id = 1;
        # no_of_pages = request.form['no_of_pages']
        ## TODO :  no of pages has to be removed
        no_of_pages=100;
        description = request.form['description']
        rating = 0
        book = Book(name=name, authors=author,content=content, section_id=section_id, librarian_id=librarian_id, no_of_pages=no_of_pages, description=description, rating=rating)
        try:
            db.session.add(book)
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))
        except Exception as error:
            print("An exception occurred:", error) # An exception occurred: 
            return str(error)
            return 'There was an issue adding the book'
    else:
        sections = Section.query.all()
        return render_template('librarian/add_book.html', sections=sections)

## Librarian edit book
@app.route('/librarian/edit_book/<int:id>', methods=['POST', 'GET'])
# @login_required
# @librarian_required
def librarian_edit_book(id):
    book = Book.query.get_or_404(id)
    sections = Section.query.all()
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
        return render_template('librarian/edit_book.html', book=book, sections = sections)

## Librarian add section
@app.route('/librarian/add_section', methods=['POST', 'GET'])
# @login_required
# @librarian_required
def librarian_add_section():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cover_image = request.files['image']

        ## TODO : get the librarian ID from the serverSide with current_user
        # librarian_id = request.form['librarian_id']
        librarian_id = 1;
        section = Section(name=name, description=description, librarian_id=librarian_id, image_filename = cover_image.filename)
        try:
            db.session.add(section)
            db.session.commit()
            if cover_image and allowed_file(cover_image.filename):
                filename = secure_filename(cover_image.filename)
                ## TODO:  Store the filename for section
                cover_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('librarian_dashboard'))
        except Exception as error:
            print("An exception occurred:", error) # An exception occurred: 
            return str(error)
            return 'There was an issue adding the section'
    else:
        return render_template('librarian/add_section.html')

## Librarian dashboard
@app.route('/librarian/dashboard')
# @login_required
# @librarian_required
def librarian_dashboard():
    ## TODO : get the librarian Id from current user
    librarian_id = 1;
    librarian  = Librarian.query.get_or_404(librarian_id)
    sections = Section.query.all()
    books_issued = librarian.books_issues;
    book_requests = []
    currently_issued = []    
    ## Get all the requests
    ## Filter ones which have a status requested and pass them as book requests    
    ## Filter ones which are currently issued
    for book_issue in books_issued:
        if(book_issue.status == "REQUESTED"):
            book_requests.append(book_issue)
        elif(book_issue.status == "ISSUED"):
            currently_issued.append(book_issue)
    ## Filter ones which librarians has added
    available_books = librarian.books
    return render_template('librarian/dashboard.html',sections = sections, book_requests = book_requests, currently_issued = currently_issued , available_books = available_books)

### USER ROUTES

## User registeration
@app.route('/user/register', methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, name=name)
        try:
            db.session.add(user)
            db.session.commit()
            # login_user(user)
            return redirect(url_for('user_dashboard'))
        except Exception as error:
            # print("An exception occurred:", error) # An exception occurred: 
            # return str(error)
            return "There was a problem adding the user"
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
            if bcrypt.checkpw(password.encode('utf-8'), user.password):
                # login_user(user)
                return redirect(url_for('user_dashboard'))
            else:
                return 'Invalid Password'
        else:
            return 'Invalid Username'
    else:
        return render_template('user/login.html')
    

## User dashboard
@app.route('/user/dashboard')
# @login_required
def user_dashboard():
    user_id = 1;
    user = User.query.get_or_404(user_id)
    books_borrowed = user.books_borrowed
    currently_borrowed = []
    ## TODO : might want to add like older borrowed book section
    for book_borrow in books_borrowed:
        if(book_borrow.status == "ISSUED"):
            currently_borrowed.append(book_borrow)
    ## get the data for the user which is connected
    return render_template('user/dashboard.html' , books_borrowed = currently_borrowed)

### BOOK ROUTES

## Get book , also them to request books
@app.route('/book/<int:id>', methods=['POST', 'GET'])
# @login_required
def book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        if book.issue:
            return 'Book already issued'

        ## TODO: get from the user ID
        user_id = 1
        book_id = id
        librarian_id = book.librarian.id
        status = "REQUESTED"
        ## MIGHT NEED TO CHECK THE USER'S BOOKS BORROWED
        ## MIGHT NEED TO ADD THE BOOKS TO THE USER'S BOOKS BORROWED
        user = User.query.get_or_404(user_id)
        total_books_borrowed = user.total_books_borrowed
        if total_books_borrowed <5:
            book_issue = BookIssue(user_id=user_id, book_id=book_id, librarian_id=librarian_id, status=status)
            try:
                db.session.add(book_issue)
                db.session.commit()
                return redirect(url_for('book', id=id))
            except:
                return 'There was an issue adding the book'
        else:        
            return 'You have reached the maximum limit of books borrowed'
        
    else:
        return render_template('book.html', book=book)

## View Book
@app.route('/user/view_book/<int:id>', methods=['POST', 'GET'])
# @login_required
# Check if user does own this book
def view_book(id):
    book = Book.query.get_or_404(id)
    ## Check if the book is indeed issued to the user
    ## If yes, then render the view_book.html
    ## Else, redirect to the book page
    return render_template('book/view.html', book=book)

## Read book
@app.route('/user/read_book/<int:id>', methods=['POST', 'GET'])
# @login_required
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
        ## TODO: get user id from current_user
        user_id = 1
        book_id = id
        content = request.form['review']
        review = Review(user_id=user_id, book_id=book_id, content=content)
        try:
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('view_book', id=id))
        except:
            return 'There was an issue adding the review'

## Issue book
@app.route('/librarian/issue_book/<int:id>', methods=['POST'])
# @login_required
# @librarian_required
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
        book_issue.date_issued = datetime.now()
        book_issue.return_date = datetime.now() + timedelta(days=7)

        ## MIGHT NEED TO ADD THE BOOKS TO THE USER'S BOOKS BORROWED
        user.total_books_borrowed += 1

        try:
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))
        except:
            return 'There was an issue issuing the book'

## Reject book
        
@app.route('/librarian/reject_book/<int:id>', methods=['POST'])
# @login_required
# @librarian_required
def reject_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page
        book_issue.status = "REJECTED"
        try:
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))
        except:
            return 'There was an issue rejecting the book request'
        
          
## Return book
@app.route('/user/return_book/<int:id>', methods=['POST'])
# @login_required
# @librarian_required
def return_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page

        current_date = datetime.now()

        if current_date > book_issue.return_date:
            book_issue.status = "REVOKED"
            return 'Return date passed, book revoked'
       
        book_issue.status = "RETURNED"

       
        try:
            db.session.delete(book_issue)
            db.session.commit()
            return redirect(url_for('user_dashboard'))
        except:
            return 'There was an issue issuing the book'
       
## Revoke book
@app.route('/librarian/revoke_book/<int:id>', methods=['POST'])
# @login_required
# @librarian_required
def revoke_book(id):
    book_issue = BookIssue.query.get_or_404(id)
    if request.method == 'POST':
        ## Check if the book is indeed issued to the user
        ## If yes, then render the view_book.html
        ## Else, redirect to the book page

        current_date = datetime.now()

        if current_date < book_issue.return_date:
            return 'Return date not yet passed , cannot revoke the book'
       
        book_issue.status = "REVOKED"
       
        try:
            db.session.delete(book_issue)
            db.session.commit()
        except:
            return 'There was an issue issuing the book'

## Remove Book 
@app.route('/librarian/remove_book/<int:id>', methods=['POST']) 
# @login_required
# @librarian_required
def remove_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        if book.issue:
            book_issue = BookIssue.query.get_or_404(book.issue.id)
            try:
                db.session.delete(book_issue)
                db.session.commit()
            except Exception as error:           
                return 'There was an issue removing the book issue'    
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as error:
            print(error)
            return 'There was an issue removing the book'       

## Remove Section
@app.route('/librarian/remove_section/<int:id>', methods=['POST'])
# @login_required
# @librarian_required
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
    
    name = request.args['search']
    books = Book.query.filter_by(Book.name.like(f"%{name}%")).all()
    return render_template('index.html', books=books)
        
## Search book by author
@app.route('/search_book_by_author', methods=['GET'])
def search_book_by_author():
    author =request.args['search']
    books = Book.query.filter_by(Book.authors.like(f"%{author}%")).all()
    return render_template('index.html', books=books)
        

## Get book for a section
@app.route('/get_section_books/<string:section>', methods=['GET'])
def get_section_books(section):
    section = Section.query.filter_by(name=section).first()
    books = section.books
    return render_template('index.html', books=books)