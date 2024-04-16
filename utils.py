import re
from string import punctuation
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


BOOKS = Book.query.all()
SECTIONS = Section.query.all()
TRANSACTIONS = Transaction.query.all()



def get_books_by_section(section_id):
    books = Book.query.filter_by(section_id=section_id).all()
    return books

def get_books_data():
    books_data = {
            i["book_id"]: {
                "title": i["title"],
                "author": i["author"],
                "section": Section.query.filter_by(section_id=i["section_id"]).first()["name"],
                "filetype": i["filetype"],
            }
            for i in BOOKS
        }
    return books_data


def get_user_books(user_id):
    trans = Transaction.query.filter_by(user_id=user_id).all()
    books_data = get_books_data()
    books = []
    for t in trans:
        book = books_data[t["book_id"]].copy()
        book["issued_at"] = t["issued_at"]
        book["tenure"] = t["tenure"]
        book["status"] = t["status"]
        books.append(book)

    return books

def get_user_feedbacks(user_id):
    for t in 
