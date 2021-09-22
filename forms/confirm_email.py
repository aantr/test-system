from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

from forms.utils.string_field import StringField


class ConfirmEmailForm(FlaskForm):
    code = StringField('Code (6 digits)', validators=[DataRequired()])
    submit = SubmitField('Confirm')
