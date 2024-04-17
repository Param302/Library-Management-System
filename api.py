from models import Section
from utils import get_books_by_section, get_sections

from app import db
from flask_restful import Resource, reqparse, fields, marshal_with


course_parser = reqparse.RequestParser()
course_parser.add_argument("course_id", type=int, required=True)
course_parser.add_argument("course_name", type=str, required=True)
course_parser.add_argument("course_code", type=str, required=True)
course_parser.add_argument("course_description", type=str)

course_fields = {
    "course_id": fields.Integer,
    "course_name": fields.String,
    "course_code": fields.String,
    "course_description": fields.String
}

section_parser = reqparse.RequestParser()
section_parser.add_argument("name", type=str, required=True)
section_parser.add_argument("description", type=str)

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
    
    @marshal_with(section_fields)
    def delete(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return {"message": "Section not found"}, 404
        db.session.delete(section)
        db.session.commit()
        return section, 200

    
    ...