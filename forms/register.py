from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Sign up')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        self.username.data = self.username.data.strip()
        self.email.data = self.email.data.strip()
        self.password.data = self.password.data.strip()
        self.repeat_password.data = self.repeat_password.data.strip()
        return True
