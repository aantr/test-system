from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired

from forms.utils.string_field import StringField


class SubmitGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add')
