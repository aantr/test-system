from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from forms.utils.string_field import StringField


class SearchUserForm(FlaskForm):
    search = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')
