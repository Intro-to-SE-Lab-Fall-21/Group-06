from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'anything'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .inboxMail import inboxMail
    from .compose import compose

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(compose, url_prefix='/')
    app.register_blueprint(inboxMail, url_prefix='/')

    from .models import User, Email

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
