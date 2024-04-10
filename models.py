from email.policy import default
from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")     # user, admin
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User {self.username} created at: {self.created_at}>"
    
    def get_id(self):
        return self.user_id

class Section(db.Model):
    __tablename__ = "sections"

    section_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Section {self.name} created at: {self.created_at}>"
    
    def get_id(self):
        return self.section_id


class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    filetype = db.Column(db.String(20), nullable=False)  # pdf, epub
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Book {self.title} added: {self.created_at}>"
    
    def get_id(self):
        return self.book_id


class Transaction(db.Model):
    __tablename__ = "transactions"

    tid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.now)
    tenure = db.Column(db.Integer, nullable=False)
    returned_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending", nullable=False)   # issued, returned, overdue, revoked, pending

    def __repr__(self):
        return f"<Transaction {self.tid} of Book Id: {self.book_id} made by User Id: {self.user_id}>"
    
    def get_id(self):
        return self.tid

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    feedback_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.tid'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    review = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Feedback {self.feedback_id} Rating: {self.rating}>"
    
    def get_id(self):
        return self.feedback_id

