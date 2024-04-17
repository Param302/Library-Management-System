import re
from string import punctuation
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from models import User, Section, Book, Transaction, Feedback

def is_valid_password(password, username):
    return (
        8 <= len(password) <= 32 
        and username not in password
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and any(c in punctuation for c in password)
    )

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
            details["issued_at"] = t.issued_at
            details["tenure"] = t.tenure
            details["status"] = t.status
            break
    return details


def get_user_transactions(user_id):
    return [t for t in get_transactions() if t.user_id == user_id]

def get_user_feedbacks(user_id):
    feedbacks = {}
    i = 0
    for t in get_user_transactions(user_id):
        if t.user_id == user_id and t.status == "returned":
            feedback = Feedback.query.filter_by(tid=t.tid).first()
            if feedback:
                book = Book.query.filter_by(book_id=t.book_id).first()
                title, author = book.title, book.author
                feedbacks[t.book_id] = {
                    "title": title,
                    "author": author,
                    "review": feedback.review,
                    "rating": feedback.rating,
                    "issued": t.issued_at,
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
        book["issued_at"] = t.issued_at
        book["tenure"] = t.tenure
        book["status"] = t.status
        if t.status == "returned" and feedbacks[t.book_id]:
            book["review"] = feedbacks[t["book_id"]]["review"]
            book["rating"] = feedbacks[t["book_id"]]["rating"]
        books.append(book)

    return books

def get_transactional_details():
    trans = get_transactions()
    books_data = get_books_data()
    details = []
    for t in trans:
        book = books_data[t.book_id].copy()
        book["issued_at"] = t.issued_at
        book["tenure"] = t.tenure
        book["status"] = t.status
        details.append(book)
    
    transactions = {"pending": [], "issued": [], "returned": [], "overdue": [], "revoked": []}
    for d in details:
        transactions[d["status"]].append(d)

    return transactions

def get_avg_rating(book_id):
    trans = [i.tid for i in get_transactions() if i.book_id == book_id and i.status == "returned"]
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