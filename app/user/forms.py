from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField, widgets, DecimalField, FileField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, NumberRange, Length
from app.models import User, Answer, Question, QuestionTopics, Topic
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from functools import partial
from wtforms.widgets import TextArea
from wtforms import Form as NoCsrfForm

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('First Name', validators=[DataRequired(), Regexp('^([A-Za-z][A-Za-z\'\-]*)$', message="Names must contain only letters and apostrophes")])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
