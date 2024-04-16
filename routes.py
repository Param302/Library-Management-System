from functools import wraps
from utils import get_books_by_section, is_valid_password, get_sections, get_user_books, get_users, get_books_data
from models import User, Section, Book, Transaction, Feedback

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user


def user_routes(app, db, bcrypt):

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for('admin_dashboard'))

        books_data = get_books_data()

        if current_user.is_authenticated:
            return render_template("index.html", books=books_data, user=current_user)
        return render_template("index.html", books=books_data)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        if current_user.is_authenticated:
            return redirect(url_for('index'))

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
    
    # @app.route('/<string:book_title>')
    @app.route('/book/<int:book_id>')
    def book(book_id):
        if current_user.is_authenticated:
            return f"Book page of {book_id} with {current_user.username}"
        return f"Book page of {book_id}"
    
    # @app.route('/<string:book_title/issue>')
    @app.route('/book/<int:book_id>/issue')
    @login_required
    @role_required("user")
    def issue_book(book_id):
        return f"Issue book page of {book_id} with {current_user.username}"
    
    # @app.route('/<string:book_title/return>')
    @app.route('/book/<int:book_id>/return')
    @login_required
    @role_required("user")
    def return_book(book_id):
        return f"Return book page of {book_id} with {current_user.username}"
    
    @app.route('/feedback', methods=['POST'])
    @login_required
    @role_required("user")
    def book_feedback():
        book_id = request.form.get('book_id')
        review = request.form.get('review')
        rating = request.form.get('rating')
        user = current_user.user_id
        return f"Feedback page of {book_id} with {current_user.username}"

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
        if current_user and current_user.is_authenticated and current_user.role != "admin":
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

    @app.route('/sections')
    @login_required
    @role_required("admin")
    def all_sections():
        sections = get_sections()
        return render_template("all_sections.html", sections=sections)

    @app.route('/section/<string:section>')
    @login_required
    @role_required("admin")
    def section(section):
        section = Section.query.filter_by(name=section).first()
        sec_books = get_books_by_section(section.section_id)
        return render_template("section.html", section=section, books=sec_books)

    # !PENDING: Adding Books in section and CRUD API of section and books

    @app.route('/book_status')
    @login_required
    @role_required("admin")
    def book_status():
        return "Books Status page"

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
