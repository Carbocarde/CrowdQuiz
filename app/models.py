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

    admin = db.Column(db.Boolean)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

    question_user = db.relationship('Question', backref='author', lazy='dynamic')
    answers_user = db.relationship('Answer', backref='author', lazy='dynamic')
    enrollment = db.relationship('Enrollment', backref='author', lazy='dynamic')

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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    image_url = db.Column(db.String(64))
    question_type = db.Column(db.String(1))

    question_answer = db.relationship('QuestionAnswer', backref='question', lazy='dynamic')

    def __repr__(self):
        return '<Question {}>'.format(self.body)

class QuestionEval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    fair = db.Column(db.Boolean)
    skipped = db.Column(db.Boolean)

    def __repr__(self):
        return '<Eval {} {}>'.format(question_id, self.fair)

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))

    # Selections in the context of the attached question
    answer_selections = db.Column(db.Integer)
    answer_presentations = db.Column(db.Integer)

    correctness_score = db.Column(db.Integer)
    correctness_votes = db.Column(db.Integer)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    answer_selections = db.Column(db.Integer)
    answer_presentations = db.Column(db.Integer)

    question_answer = db.relationship('QuestionAnswer', backref='answer', lazy='dynamic')

    def __repr__(self):
        return '<Answer {}, Correct: {}>'.format(self.body, self.correct)

    def __str__(self):
        return '{}'.format(self.body)

# For when an answer is reported
class AnswerReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class QuestionAnswerArgument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_answer = db.relationship('QuestionAnswer', backref='answer_argument', lazy='dynamic')

    body = db.Column(db.String(140))

    argument_votes = db.Column(db.Integer)
    argument_evaluations = db.Column(db.Integer)

# For when an argument is reported
class QuestionAnswerArgumentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class TFQuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    selected_true = db.Column(db.Boolean)
    # disagreed with the given answer
    disagreed = db.Column(db.Boolean)

class MCQuestionAttempt(db.Model):
    __tablename__ = 'mcquestionattempt'

    id = db.Column(db.Integer, primary_key=True)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class MCQuestionChoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    mc_question_attempt_id = db.Column(db.Integer, db.ForeignKey('mcquestionattempt.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))

    selected = db.Column(db.Boolean)

    mc_question_attempt = db.relationship('MCQuestionAttempt', backref='mc_question_attempt', lazy='dynamic')

class OpenEndedQuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'))

    body = db.Column(db.String(140))
    # When presented with the "correct" answer, graded themselves as correct
    graded_correct = db.Column(db.Boolean)

class QuestionTopics(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    connection_score = db.Column(db.Integer)
    evaluations = db.Column(db.Integer)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.String(40))

    question_topic = db.relationship('QuestionTopics', backref='topic', lazy='dynamic')
    exam_topic = db.relationship('ExamTopics', backref='topic', lazy='dynamic')

    def __repr__(self):
        return '<Topic {}>'.format(self.body)

    def __str__(self):
        return '{}'.format(self.body)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))

    body = db.Column(db.String(40))

    exam_topic = db.relationship('ExamTopics', backref='exam', lazy='dynamic')

class ExamTopics(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    connection_score = db.Column(db.Integer)
    evaluations = db.Column(db.Integer)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    # Suggestor
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    approved = db.Column(db.Boolean)
    body = db.Column(db.String(64))
    description = db.Column(db.String(140))

    enrollment = db.relationship('Enrollment', backref='class', lazy='dynamic')

    def __repr__(self):
        return '<Subject: {}>'.format(self.body)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.String(64))

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
