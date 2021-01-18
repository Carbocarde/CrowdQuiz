from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField, widgets, DecimalField, FileField, IntegerField, RadioField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, NumberRange, Length
from app.models import User, Answer, Question, QuestionTopics, Topic
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from functools import partial
from wtforms.widgets import TextArea
from wtforms import Form as NoCsrfForm

class AddExamForm(FlaskForm):
    exam_title = StringField('Exam Name', description="Ex: Exam 2", validators=[DataRequired(), Length(max=40)])
    exam_number = IntegerField('Exam Number', validators=[NumberRange(min=1, message='Please enter a non-negative number')])
    #exam_date = DateField('Exam Date', description='Format: day-month-year')
    cumulative = BooleanField('Cumulative Exam?', description="Note: this means that all prior content is fair game on this exam and students should study prior material about as much as the new content")

    topics = StringField('Exam Topics', description="Ex: Addition, Order of Operations, Division")

    submit = SubmitField('Submit')

class EditExamForm(FlaskForm):
    exam_title = StringField('Exam Name', description="Ex: Exam 2", validators=[DataRequired(), Length(max=40)])
    exam_number = IntegerField('Exam Number', validators=[NumberRange(min=1, message='Please enter a non-negative number')])
    #exam_date = DateField('Exam Date', description='Format: day-month-year')
    cumulative = BooleanField('Cumulative Exam?', description="Note: this means that all prior content is fair game on this exam and students should study prior material about as much as the new content")

    topics = StringField('Exam Topics', description="Ex: Addition, Order of Operations, Division")

    submit = SubmitField('Submit')
