import os
import requests
from functools import wraps
from utils import allowed_file, get_book_details, get_book_details_for_user, get_books_by_section, get_transactional_details, get_transactions, is_valid_password, get_sections, get_user_books, get_users, get_books_data
from models import User, Section, Book, Transaction, Feedback

from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user


def user_routes(app, db, bcrypt):

    @app.route('/')
    def index():
        books_data = get_books_data()

        if current_user.is_authenticated:
            return render_template("index.html", books=books_data, user=current_user)
        return render_template("index.html", books=books_data)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == "GET":
            return render_template("login.html")

        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, role="user").first()
        if not user:
            return render_template("login.html", user_not_found=True, username=username)

        if not bcrypt.check_password_hash(user.password, password):
            return render_template("login.html", invalid_credentials=True)

        login_user(user)
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    @role_required("user")
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == "GET":
            return render_template("register.html")

        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        conf_password = request.form.get('confirm_password')

        if not is_valid_password(password, username):
            return render_template("register.html", incomplete_pass=True)

        if password != conf_password:
            return render_template("register.html", password_mismatch=True)

        user = User.query.filter_by(username=username, role="user").first()
        if user:
            return render_template("register.html", user_exists=True, username=username)

        email_exists = User.query.filter_by(email=email, role="user").first()
        if email_exists:
            return render_template("register.html", user_exists=True, email=email)

        user = User(name=name, username=username, email=email,
                    password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()

        return render_template("register.html", success=True)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route('/dashboard')
    @login_required
    @role_required("user")
    def dashboard():
        books = get_user_books(current_user.user_id)
        return render_template("dashboard.html", user=current_user, books=books)

    @app.route('/book/<int:book_id>')
    def book(book_id):
        book = get_book_details(book_id)
        if current_user.is_authenticated and current_user.role == "user":
            book = get_book_details_for_user(current_user.user_id, book_id)
        return render_template("book.html", book=book, user=current_user)

    @app.route('/book/<int:book_id>/issue', methods=['GET', 'POST'])
    @login_required
    @role_required("user")
    def issue_book(book_id):
        if request.method=="GET":
            return redirect(f"/book/{book_id}")
        days = request.form.get("days")
        # transaction = Transaction.query.filter_by(user_id=current_user.user_id, book_id=book_id).first()
        # if transaction:
        #     return redirect(f"/book/{book_id}")
        transaction = Transaction(user_id=current_user.user_id, book_id=book_id, tenure=days)
        db.session.add(transaction)
        db.session.commit()
        return redirect(f"/book/{book_id}")

    @app.route('/book/<int:book_id>/return', methods=['GET', 'POST'])
    @login_required
    @role_required("user")
    def return_book(book_id):
        if request.method=="GET":
            return redirect(f"/book/{book_id}")
        
        review = request.form.get("review", "")
        rating = request.form.get("rating")
        transaction = Transaction.query.filter_by(user_id=current_user.user_id, book_id=book_id).order_by(Transaction.issued_at.desc()).first()
        transaction.status = "returned"
        feedback = Feedback(transaction_id=transaction.tid, review=review, rating=rating)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/book/{book_id}")

    @app.route('/profile')
    @login_required
    @role_required("user")
    def profile():
        user_books = get_user_books(current_user.user_id)
        return render_template("profile.html", user=current_user, user_books=user_books)

    @app.route('/u/@<string:username>')
    def user_profile(username):
        user = User.query.filter_by(username=username).first()
        user_books = get_user_books(user.user_id)
        return render_template("user_profile.html", user=user, user_books=user_books)


def librarian_routes(app, db, bcrypt):

    @app.route('/admin', methods=['GET', 'POST'])
    def admin():    # Admin123*
        if current_user and current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))

        if request.method == "GET":
            return render_template("admin_login.html")

        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, role="admin").first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return render_template("admin_login.html", invalid_credentials=True)
        login_user(user)

        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/dashboard')
    @login_required
    @role_required("admin")
    def admin_dashboard():
        users = get_users()
        return render_template("admin_dash.html", admin=current_user, users=users)

    @app.route('/sections', methods=['GET', 'POST'])
    @login_required
    @role_required("admin")
    def all_sections():
        code = None
        if request.method == "POST":
            if request.form.get("name"):    # For Adding a section
                req = requests.post("http://localhost:5000/api/section",
                                    json=request.form.to_dict(), headers={'Content-Type': 'application/json'})
            else:                           # For Deleting a section
                req = requests.delete(f"http://localhost:5000/api/section/{request.form.get('section_id')}", json=request.form.to_dict(
                ), headers={'Content-Type': 'application/json'})

            code = req.status_code
        sections = get_sections()
        return render_template("all_sections.html", sections=sections, code=code)

    # !PENDING: Adding Books in section and CRUD API of section and books

    @app.route('/s/<int:section_id>', methods=['GET', 'POST'])
    @login_required
    @role_required("admin")
    def section(section_id):
        file_code = None
        section = Section.query.get(section_id)
        if not section:
            return redirect(url_for('all_sections'))
        if request.method == "POST":
            if request.form.get("title"):   # For Adding a book
                file = request.files["file"]
                filename, filetype = file.filename.split(".")
                data = {
                    "title": request.form.get("title"),
                    "author": request.form.get("author"),
                    "section_id": section_id,
                    "filetype": filetype
                }

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(filepath):
                        file_code = 409      # File already exists
                    else:
                        data["filename"] = filename
                        req = requests.post(
                            f"http://localhost:5000/api/book/upload", json=data, headers={'Content-Type': 'application/json'})
                        file_code = req.status_code
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    file_code = -1      # Invalid file type
            
            else:       # Deleting a book
                req = requests.delete(f"http://localhost:5000/api/book/{request.form.get('book_id')}", json=request.form.to_dict(
                ), headers={'Content-Type': 'application/json'})
                file_code = req.status_code

        req = requests.get(f"http://localhost:5000/api/section/{section_id}")

        return render_template("section.html", section=section, books=req.json(), file_code=file_code)

    @app.route('/book_status')
    @login_required
    @role_required("admin")
    def book_status():
        trans = get_transactional_details()
        return render_template("book_status.html", admin=current_user, transactions=trans)

    @app.route('/users')
    @login_required
    @role_required("admin")
    def all_users():
        users = get_users()
        return render_template("all_users.html", admin=current_user, users=users)


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                # !NOTE: Changes so that user can login and then redirect to the original page
                # For admin, redirect to admin page
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
