from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ActionLinkForm(FlaskForm):
    str_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Join')
