from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, SelectMultipleField, widgets, DecimalField, FileField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, NumberRange, Length
from app.models import User, Answer, Question, QuestionTopics, Topic
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from functools import partial
from wtforms.widgets import TextArea
from wtforms import Form as NoCsrfForm

class EditExamStructureForm(FlaskForm):
    exams = IntegerField('Number of Exams (Excluding Final Exam)', validators=[NumberRange(min=0, message='Please enter a non-negative number')])
    quizzes = IntegerField('Number of Quizzes', validators=[NumberRange(min=0, message='Please enter a non-negative number')])
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

class ProposeSectionForm(FlaskForm):
    body = StringField('Section ID', description="Ex: G07", validators=[DataRequired(), Length(max=40)])
    description = StringField('Section Description', description="Ex: Taught by Professor O'Neill", widget=TextArea(), validators=[DataRequired(), Length(max=140)])

    submit = SubmitField('Submit')

class ProposeTopicForm(FlaskForm):
    body = StringField('Topic Name', description="Ex: Social Construction of Reality", validators=[DataRequired(), Length(max=40)])
    description = StringField('Topic Description (optional)', widget=TextArea(), validators=[Length(max=140)])

    submit = SubmitField('Submit')

# DO NOT DISPLAY AS SOLO FORM, MUST BE SUBFORM
class EvaluateQuestionSubForm(NoCsrfForm):
    fair = BooleanField('Fair Question', default=True)
    accurate_topics = BooleanField('Correct topics', default=True)
    skip = BooleanField('Skip Question Evaluation', default=True)

class NewQuestionSubForm(FlaskForm):
    """Main question form"""

    question = StringField('Question', validators=[DataRequired()])

    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    incorrect_answer_1 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_2 = StringField('Incorrect Answer', validators=[DataRequired()])
    incorrect_answer_3 = StringField('Incorrect Answer', validators=[DataRequired()])

    #topics = QuerySelectMultipleField()

class ContributeForm(FlaskForm):
    evaluate_entries = FieldList(FormField(EvaluateQuestionSubForm))
    submit = SubmitField('Submit')

class NewQuestionForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])

    correct_answer = StringField('Correct Answer', widget=TextArea(), validators=[DataRequired(), Length(max=140)])

    submit = SubmitField('Submit')

    def validate_question(self, question):
        from flask_login import current_user
        question = Question.query.filter_by(body=question.data).first()
        if question is not None and question.author.id == current_user.id:
            raise ValidationError('Please submit a different question.')

"""
class AnswerForm(FlaskForm):
    # Subform
    answer_text = StringField('Incorrect Answer', validators=[DataRequired()])
    correct_answer = BooleanField("Valid/Correct Answer")
"""

"""
class NewQuestionForm(FlaskForm):
    '''Main question form'''

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
            raise ValidationError('Identical subject question found! Please try entering a different question')"""

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
