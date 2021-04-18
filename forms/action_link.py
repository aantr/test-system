from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ActionLinkForm(FlaskForm):
    str_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Proceed')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        self.str_id.data = self.str_id.data.strip()
        return True
