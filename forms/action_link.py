from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from forms.utils.string_field import StringField


class ActionLinkForm(FlaskForm):
    str_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Proceed')
