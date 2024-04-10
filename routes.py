from functools import wraps
from models import User, Section, Book, Transaction, Feedback

from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user

def user_routes(app, db, bcrypt):

    @app.route('/')
    def index():
        return "Home page"
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return "Login page"

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        return "Register page"
    
    @app.route('/logout')
    @login_required
    def logout():
        return "Logout page"
    

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return "Dashboard page"
    
    @app.route('/book')
    @login_required
    def book():
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
                return redirect(url_for('index'), 305)
            return func(*args, **kwargs)
        return wrapper
    return decorator