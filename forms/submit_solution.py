from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField
from wtforms.validators import DataRequired
from forms.utils.text_area_field import TextAreaField


class SubmitSolutionForm(FlaskForm):
    text = TextAreaField('Input source code here', validators=[])
    file = FileField('Select file', validators=[])
    select = SelectField('Select programming language', validators=[DataRequired()])
    submit = SubmitField('Send')
