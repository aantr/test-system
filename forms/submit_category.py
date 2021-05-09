from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired

from forms.utils.string_field import StringField


class SubmitCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add')
