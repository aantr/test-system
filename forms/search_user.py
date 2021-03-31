from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SearchUserForm(FlaskForm):
    search = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')
