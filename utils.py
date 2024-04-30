from datetime import datetime, timedelta
import os
import random
import re
from string import ascii_letters, digits, punctuation

from flask import url_for
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from models import Purchase, User, Section, Book, Transaction, Feedback
from pdf2image import convert_from_path
from PIL import Image

def is_valid_password(password, username):
    return (
        8 <= len(password) <= 32 
        and username not in password
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and any(c in punctuation for c in password)
    )

def generate_string(length=12):
    return "".join(random.choices(ascii_letters + digits, k=length))


def get_users():
    return User.query.filter_by(role="user").all()

def get_books():
    return Book.query.all()

def get_sections():
    return Section.query.all()

def get_transactions():
    return Transaction.query.order_by(Transaction.tid.desc()).all()

def get_books_by_section(section_id):
    books = Book.query.filter_by(section_id=section_id).all()
    return books

def get_book_details(book_id):
    book = Book.query.filter_by(book_id=book_id).first()
    return {
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "section": Section.query.filter_by(section_id=book.section_id).first().name,
        "filename": book.filename,
        "filetype": book.filetype,
    }

def get_books_data():
    books_data = {
            i.book_id: get_book_details(i.book_id)
            for i in get_books()
        }
    return books_data

def get_book_details_for_user(user_id, book_id):
    book_details = get_book_details(book_id)
    trans = get_user_transactions(user_id)

    details = book_details.copy()
    for t in trans:
        if t.book_id == book_id and t.status != "returned":
            details["issued_at"] = t.issued_at.strftime("%d %b'%y")
            details["tenure"] = t.tenure
            details["status"] = t.status
            break
    if has_user_purchased_book(user_id, book_id):
        details["status"] = "bought"
    return details


def get_user_transactions(user_id):
    return [t for t in get_transactions() if t.user_id == user_id]

def get_user_feedbacks(user_id):
    feedbacks = {}
    i = 0
    for t in get_user_transactions(user_id):
        if t.user_id == user_id and t.status in ("returned", "bought"):
            feedback = Feedback.query.filter_by(transaction_id=t.tid).first()
            if feedback:
                book = Book.query.filter_by(book_id=t.book_id).first()
                title, author = book.title, book.author
                feedbacks[t.book_id] = {
                    "title": title,
                    "author": author,
                    "review": feedback.review,
                    "rating": feedback.rating,
                    "issued": str(t.issued_at.strftime("%d %b'%y")),
                }
                i += 1
    
    return feedbacks

def get_user_books(user_id):
    trans = get_user_transactions(user_id)
    books_data = get_books_data()
    feedbacks = get_user_feedbacks(user_id)
    books = []
    for t in trans:
        book = books_data[t.book_id].copy()
        book["issued_at"] = t.issued_at.strftime("%d %b'%y")
        book["tenure"] = t.tenure
        book["status"] = t.status
        if t.status in ("returned", "bought"):
            if t.status == "returned":
                if t.returned_at is not None:
                    book["returned_at"] = t.returned_at.strftime("%d %b'%y")
                else:
                    book["returned_at"] = (t.issued_at + timedelta(days=6)).strftime("%d %b'%y")
            if t.book_id in feedbacks:
                book["review"] = feedbacks[t.book_id]["review"]
                book["rating"] = feedbacks[t.book_id]["rating"]
        books.append(book)

    return books

def get_transactional_details():
    trans = get_transactions()
    books_data = get_books_data()
    details = []
    for t in trans:
        user = User.query.filter_by(user_id=t.user_id).first()
        book = books_data[t.book_id].copy()
        book["user_id"] = t.user_id
        book["username"] = user.username
        book["name"] = user.name
        book["trans_id"] = t.tid
        book["issued_at"] = t.issued_at.strftime("%d %b'%y")
        book["tenure"] = t.tenure
        book["status"] = t.status
        if t.status == "overdue":
            book["overdue"] = (t.issued_at + timedelta(days=t.tenure)).strftime("%d %b'%y")
        elif t.status == "returned":
            if t.returned_at is not None:
                book["returned_at"] = t.returned_at.strftime("%d %b'%y")
            else:
                book["returned_at"] = (t.issued_at + timedelta(days=6)).strftime("%d %b'%y")
        details.append(book)
    
    transactions = {"pending": [], "issued": [], "returned": [], "overdue": [], "bought": []}
    for d in details:
        transactions[d["status"]].append(d)

    return transactions

def get_avg_rating(book_id):
    trans = [i.tid for i in get_transactions() if i.book_id == book_id and i.status in ("returned", "bought")]
    total_rating = 0
    n = 0
    for t in trans:
        feedback = Feedback.query.filter_by(transaction_id=t).first()
        if feedback:
            n += 1
            total_rating += feedback["rating"]
  
    return total_rating / n if n else 0


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def has_user_purchased_book(user_id, book_id):
    trans = [t.tid for t in get_transactions() if t.book_id == book_id and t.user_id == user_id and t.status == "bought"]

    return False if not trans else trans[0]


def get_book_download_code(user_id, book_id):
    if not (trans_id:=has_user_purchased_book(user_id, book_id)):
        return None
    
    return Purchase.query.filter_by(transaction_id=trans_id).first().download_code

def within_download_period(book_id, user_id, transactions):
    purchase_time = transactions[(user_id, book_id)][0]
    current_time = datetime.now()
    time_difference = current_time - purchase_time

    if time_difference > timedelta(hours=24):
        del transactions[(user_id, book_id)]
        return False
    return True

def finish_transaction(user, book_id, db, review, rating):
    transaction = Transaction.query.filter_by(user_id=user.user_id, book_id=book_id, status="issued").order_by(Transaction.issued_at.desc()).first()
    transaction.returned_at = datetime.now()
    transaction.status = "returned"
    store_review(review, rating, transaction.tid, db)


def store_review(review, rating, trans_id, db):
    feedback = Feedback(transaction_id=trans_id, review=review, rating=rating)
    db.session.add(feedback)
    db.session.commit()

def process_path(file_path):
    folder, name = file_path.rsplit("/", 1)
    name = name.rsplit(".", 1)[0]
    img_folder = os.path.join(os.getcwd(), "static", "thumbnails/")
    os.makedirs(img_folder, exist_ok=True)
    return folder, name, img_folder

def remove_book_thumbnail(filepath):
    _, name, img_folder = process_path(filepath)
    os.remove(img_folder + name + ".jpg")

def pdf_to_image(pdf_path):
    folder, name, img_folder = process_path(pdf_path)
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    first_page = pages[0]
    first_page.save(img_folder + name + ".jpg", "JPEG")

def epub_to_image(epub_path):
    ...
