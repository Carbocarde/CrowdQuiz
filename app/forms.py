from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField, widgets, DecimalField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, NumberRange, Length
from app.models import User, Answer, Question, QuestionTopics, Topic
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from functools import partial
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired(), Regexp('^([A-Za-z][A-Za-z\'\-]*)$', message="Names must contain only letters and apostrophes")])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    school = QuerySelectField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditExamStructureForm(FlaskForm):
    exams = DecimalField('Number of Exams (Excluding Final Exam)', validators=[DataRequired("Please enter a number"), NumberRange(min=0, message='Please enter a non-negative number')])
    quizzes = DecimalField('Number of Quizzes', validators=[DataRequired("Please enter a number"), NumberRange(min=0, message='Please enter a non-negative number')])
    final_exam = BooleanField('Final Exam?')
    final_exam_cumulative = BooleanField('Final Exam Cumulative?')
    comment = StringField('Comments? (Optional)', widget=TextArea(), validators=[Length(max=140)])
    #syllabus = FileField('Syllabus Exam Structure Screenshot (optional)')

    submit = SubmitField('Submit')

class ProposeClassForm(FlaskForm):
    body = StringField('Class ID', description="Ex: SOC 1101", validators=[DataRequired(), Length(max=40)])
    title = StringField('Class Name', description="Ex: Sociology", validators=[DataRequired(), Length(max=40)])
    description = StringField('Class Description', description="Ex: The study of the development, structure, and functioning of human society.", widget=TextArea(), validators=[DataRequired(), Length(max=140)])

    submit = SubmitField('Submit')

class ProposeTopicForm(FlaskForm):
    body = StringField('Topic Name', description="Ex: Social Construction of Reality", validators=[DataRequired(), Length(max=40)])
    description = StringField('Topic Description (optional)', widget=TextArea(), validators=[Length(max=140)])

    submit = SubmitField('Submit')

class EvaluateQuestionForm(FlaskForm):
    fair = BooleanField('Fair Question')
    accurate_topics = BooleanField('Correct topics')

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


class NewQuestionForm(FlaskForm):
    """Main question form"""

    question = StringField('Question', validators=[DataRequired()])

    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    incorrect_answer_1 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_2 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_3 = StringField('Incorrect Answer', validators=[DataRequired()])

    topics = QuerySelectMultipleField()

    submit = SubmitField('Submit New Question')

    def __init__(self, subject, *args, **kwargs):
        super(NewQuestionForm, self).__init__(*args, **kwargs)
        self.subject = subject

    def validate_question(self, question):
        question = Question.query.filter_by(subject=self.subject).filter_by(body=self.question.data).first()
        if question is not None:
            raise ValidationError('Identical subject question found! Please try entering a different question')

class NewSubjectForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])

    description = StringField('Description', validators=[DataRequired()])

    topics = StringField('Initial Subtopic', validators=[DataRequired()])

    submit = SubmitField('Submit New Question')

    def validate_question(self, question):
        subjectduplicate = Subject.query.filter_by(body=self.subject).filter_by(body=self.question.data).first()
        if subjectduplicate is not None:
            raise ValidationError('Identical subject found! Please try entering a different subject or go follow that subject!')


class NewTopicForm(FlaskForm):
    topic = StringField('New Subtopic', validators=[DataRequired()])
    submit = SubmitField('Submit New Subtopic')

class DeleteQuestionForm(FlaskForm):
    cancel = SubmitField('Cancel')
    submit = SubmitField('Delete Question Permanently')

QueryRadioField = partial(
    QuerySelectField,
    widget=widgets.ListWidget(prefix_label=False),
    option_widget=widgets.RadioInput(),
)

QueryCheckboxField = partial(
    QuerySelectMultipleField,
    widget=widgets.ListWidget(prefix_label=False),
    option_widget=widgets.CheckboxInput(),
)

class QuizQuestion(FlaskForm):
    answers = QueryRadioField("",
        render_kw={"class":"btn-group-vertical"})
    submit = SubmitField('Submit Answer',
        render_kw={"class":"btn btn-primary"})

class ReviewQuestionForm(FlaskForm):

    fair = SubmitField('Fair Question')
    unfair = SubmitField('Unfair Question')
    skip = SubmitField('Skip')
