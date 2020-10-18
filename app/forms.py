from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Answer, Question, QuestionTopics

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

"""
class AnswerForm(FlaskForm):
    # Subform
    answer_text = StringField('Incorrect Answer', validators=[DataRequired()])
    correct_answer = BooleanField("Valid/Correct Answer")
"""

class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """
    def pre_validate(self, form):
        pass

class NewQuestionForm(FlaskForm):
    """Main question form"""

    question = StringField('Question', validators=[DataRequired()])

    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    incorrect_answer_1 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_2 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_3 = StringField('Incorrect Answer', validators=[DataRequired()])

    topics = NonValidatingSelectMultipleField(SelectMultipleField('Topics'))

    submit = SubmitField('Submit New Question')

    """def __init__(self, topics, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.possible_tags = topics"""
