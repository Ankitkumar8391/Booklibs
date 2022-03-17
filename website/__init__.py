from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"
PASSWORD = "admin@lms"


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)

def start_app():
    app = Flask(__name__)
    app.secret_key = 'This is a Secret Key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from . views import views, page_not_found
    from . api import api
    from . books import books
    from . members import member
    from .models import Books, Members, Issued,Payment

    create_database(app)
    db.create_all(app=app)

    app.register_error_handler(404, page_not_found)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(books, url_prefix='/books')
    app.register_blueprint(member, url_prefix='/members')
    return app