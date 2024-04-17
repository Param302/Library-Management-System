from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# api = Api()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
    app.secret_key = "Some key"

    db.init_app(app)
    api = Api(app)
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager(app)

    from models import User
    from api import SectionAPI
    from routes import user_routes, librarian_routes

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return "You must be logged in to access this page", 403
    

    user_routes(app, db, bcrypt)
    librarian_routes(app, db, bcrypt)

    api.add_resource(SectionAPI, '/api/section', '/api/section/<int:section_id>')

    return app