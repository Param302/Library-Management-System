def user_routes(app, db, bcrypt):

    @app.route('/')
    def home():
        return "Home page"
    ...


def librarian_routes(app, db, bcrypt):
    ...