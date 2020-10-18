from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from time import time
import jwt
from app import app

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    questions = db.relationship('Question', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class QuestionTopics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('Answer', backref='question', lazy='dynamic')
    subject = db.Column(db.Integer, db.ForeignKey('subject.id'))
    topics = db.relationship('QuestionTopics', backref='topics', lazy='dynamic')

    def __repr__(self):
        return '<Question {}>'.format(self.body)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    correct = db.Column(db.Boolean)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __repr__(self):
        return '<Answer {}, Correct: {}>'.format(self.username, self.correct)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))

    def __repr__(self):
        return '<Subject: {}>'.format(self.body)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(40))
    subject = db.Column(db.Integer, db.ForeignKey('subject.id'))
    topics = db.relationship('QuestionTopics', backref='questions', lazy='dynamic')


    def __repr__(self):
        return '<Topic {}>'.format(self.body)
