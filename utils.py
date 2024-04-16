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

def get_user_transactions(user_id):
    return [t for t in TRANSACTIONS if t["user_id"] == user_id]

def get_user_books(user_id):
    trans = get_user_transactions(user_id)
    books_data = get_books_data()
    feedbacks = get_user_feedbacks(user_id)
    books = []
    for t in trans:
        book = books_data[t["book_id"]].copy()
        book["issued_at"] = t["issued_at"]
        book["tenure"] = t["tenure"]
        book["status"] = t["status"]
        if t["status"] == "returned" and feedbacks[t["book_id"]]:
            book["review"] = feedbacks[t["book_id"]]["review"]
            book["rating"] = feedbacks[t["book_id"]]["rating"]
        books.append(book)

    return books

def get_user_feedbacks(user_id):
    feedbacks = {}
    i = 0
    for t in get_user_transactions(user_id):
        if t["user_id"] == user_id and t["status"] == "returned":
            feedback = Feedback.query.filter_by(tid=t["tid"]).first()
            if feedback:
                title, author = [(b["title"], b["author"]) for b in BOOKS if b["book_id"] == t["book_id"]][0]
                feedbacks[t["book_id"]] = {
                    "title": title,
                    "author": author,
                    "review": feedback["review"],
                    "rating": feedback["rating"],
                    "issued": t["issued_at"],
                }
                i += 1
    
    return feedbacks

