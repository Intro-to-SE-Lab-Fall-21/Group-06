from . import db
from flask_login import UserMixin


class Email(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    subject = db.Column(db.String(250))
    message = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    emails = db.relationship('Email')
