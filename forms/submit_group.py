from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired

from forms.utils.multiply_checkbox_field import MultiplyCheckboxField


class SubmitGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add')
