from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        self.username.data = self.username.data.strip()
        self.password.data = self.password.data.strip()
        return True
