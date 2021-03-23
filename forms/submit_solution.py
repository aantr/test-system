from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired


class SubmitSolutionForm(FlaskForm):
    text = TextAreaField('Input source code here', validators=[])
    file = FileField('Select file', validators=[])
    select = SelectField('Select programming language', validators=[DataRequired()])
    submit = SubmitField('Send')
