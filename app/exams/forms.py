from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField, widgets, DecimalField, FileField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, NumberRange, Length
from app.models import User, Answer, Question, QuestionTopics, Topic
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from functools import partial
from wtforms.widgets import TextArea
from wtforms import Form as NoCsrfForm

class ExamShortAnswerQuestion(FlaskForm):
    answer = StringField('Answer', widget=TextArea(), validators=[DataRequired(),Length(max=140)])
    submit = SubmitField("Submit")
