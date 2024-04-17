import os
from models import Book, Section
from utils import get_books_by_section, UPLOAD_FOLDER

from app import db
from flask_restful import Resource, reqparse, fields, marshal_with

section_parser = reqparse.RequestParser()
section_parser.add_argument("name", type=str, required=True)
section_parser.add_argument("description", type=str)

books_parser = reqparse.RequestParser()
books_parser.add_argument("title", type=str, required=True)
books_parser.add_argument("author", type=str, required=True)
books_parser.add_argument("section_id", type=int, required=True)
books_parser.add_argument("filename", type=str, required=True)
books_parser.add_argument("filetype", type=str, required=True)

section_fields = {
    "section_id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "created_at": fields.DateTime
}

section_books_fields = {
    "book_id": fields.Integer,
    "title": fields.String,
    "author": fields.String,
    "section_id": fields.Integer,
    "filename": fields.String,
    "filetype": fields.String,
    "created_at": fields.DateTime
}

book_field = {
    "book_id": fields.Integer,
    "title": fields.String,
    "author": fields.String,
    "section_id": fields.Integer,
    "filename": fields.String,
    "filetype": fields.String,
    "created_at": fields.DateTime
}

class SectionAPI(Resource):
    @marshal_with(section_books_fields)
    def get(self, section_id):
        section = Section.query.get(section_id)
        section_books = get_books_by_section(section_id)
        if not section:
            return {"message": "Section not found"}, 404
        return section_books, 200
    
    @marshal_with(section_fields)
    def post(self):
        args = section_parser.parse_args()
        name = args.get("name")
        description = args.get("description", "")
        section = Section.query.filter_by(name=name).first()
        if section:
            return {"message": "Section already exists"}, 409
        
        section = Section(name=name, description=description)
        db.session.add(section)
        db.session.commit()
        return section, 201
    
    def delete(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return {"message": "Section not found"}, 404
        db.session.delete(section)
        db.session.commit()
        return 200


class BookAPI(Resource):

    def get(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        return book, 200
    
    @marshal_with(book_field)
    def post(self):
        args = books_parser.parse_args()
        title = args.get("title")
        author = args.get("author")
        section_id = args.get("section_id")
        filename = args.get("filename")
        filetype = args.get("filetype")
        book = Book.query.filter_by(title=title, author=author).first()
        if book:
            return {"message": "Book already exists"}, 409
        book = Book(title=title, author=author, section_id=section_id, filename=filename, filetype=filetype)
        db.session.add(book)
        db.session.commit()

        return book, 201
    
    def delete(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        os.remove(os.path.join(UPLOAD_FOLDER, book.filename))
        db.session.delete(book)
        db.session.commit()
        return 200