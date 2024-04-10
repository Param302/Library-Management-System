from functools import wraps
from utils import is_valid_password
from models import User, Section, Book, Transaction, Feedback

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user, user_logged_in

def user_routes(app, db, bcrypt):

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            return render_template("index.html", user=current_user)
        return render_template("index.html")
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "GET":
            return render_template("login.html")
        
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("login.html", user_not_found=True, username=username)
        
        if not bcrypt.check_password_hash(user.password, password):
            return render_template("login.html", invalid_credentials=True)
        
        login_user(user)
        return redirect(url_for('dashboard'))

    @app.route('/register', methods=['GET', 'POST'])
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

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", user_exists=True, username=username)
        
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return render_template("register.html", user_exists=True, email=email)
        
        user = User(name=name, username=username, email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
    
        return render_template("register.html", success=True)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return f"You've been logged out successfully!"
    

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return "Dashboard page"
    
    @app.route('/book/<int:book_id>')
    @login_required
    def book(book_id):
        return "Book page"

    @app.route('/profile')
    @login_required
    def profile():
        return "Profile page"
    ...


def librarian_routes(app, db, bcrypt):

    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        return "Admin login page"
    
    @app.route('/panel')
    @login_required
    @role_required("admin")
    def admin_dashboard():
        return "Admin dashboard page"
    
    @app.route('/sections')
    @login_required
    @role_required("admin")
    def all_sections():
        return "Sections page"
    
    @app.route('/sections/<int:section_id>')
    @login_required
    @role_required("admin")
    def section(section_id):
        return f"Section page of {section_id}"
    
    @app.route('/book_status')
    @login_required
    @role_required("admin")
    def book_status():
        return "Books Status page"
    
    @app.route('/users')
    @login_required
    @role_required("admin")
    def users():
        return "Users page"
    ...


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator