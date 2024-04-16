from utils import get_sections

from flask_restful import Resource


class Section(Resource):
    def get(self):
        return {"sections": get_sections()}
    
    def post(self):
        pass

    
    ...