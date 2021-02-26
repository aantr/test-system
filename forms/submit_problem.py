from copy import copy, deepcopy

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, TextAreaField, FileField, SelectField, IntegerField, MultipleFileField
from wtforms.validators import DataRequired, NumberRange

from program_testing.test_program import TestProgram


class SubmitProblemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    task_text = TextAreaField('Task text', validators=[DataRequired()])
    file = FileField('Tests (zip archive)', validators=[DataRequired()])
    time = IntegerField('Time limit (in milliseconds)', validators=[
        DataRequired(), NumberRange(min=50)])
    memory = IntegerField('Memory limit (in kilobytes)', validators=[
        DataRequired(), NumberRange(min=1024)])
    submit = SubmitField('Add')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if not TestProgram.check_tests_zip(deepcopy(self.file.data.stream).read()):
            self.file.errors.append('Incorrect zip archive format')
            return False
        return True
