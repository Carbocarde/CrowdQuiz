from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired, Regexp
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('First Name', validators=[DataRequired(), Regexp('^([A-Za-z][A-Za-z\'\-]*)$', message="Names must contain only letters and apostrophes")])
    school = QuerySelectField()
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
