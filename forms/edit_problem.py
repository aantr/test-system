from copy import deepcopy

from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, FileField, IntegerField, \
    MultipleFileField
from wtforms.validators import DataRequired, NumberRange

from data.image import Image
from data.problem_tests import ProblemTests
from forms.utils.multiply_checkbox_field import MultiplyCheckboxField
from forms.utils.string_field import StringField
from program_testing.test_program import TestProgram
from utils.utils import allowed_file


class EditProblemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    task_text = TextAreaField('Task', validators=[DataRequired()])
    images = MultipleFileField('Images', validators=[])
    input_text = TextAreaField('Input', validators=[])
    output_text = TextAreaField('Output', validators=[])
    examples = TextAreaField('Examples', validators=[])
    note = TextAreaField('Note', validators=[])
    categories = MultiplyCheckboxField('problem_category', 'Categories')

    file = FileField('Tests (zip archive)', validators=[])
    time = IntegerField('Time limit (in milliseconds)', validators=[
        DataRequired(), NumberRange(min=50)])
    memory = IntegerField('Memory limit (in kilobytes)', validators=[
        DataRequired(), NumberRange(min=1024)])
    submit = SubmitField('Save')

    example_split_tag = '<example>'
    example_data_tag = '<data>'

    def validate(self):
        self.categories.checked = []
        for i in self.categories.choices:
            if self.categories.prefix_id + i[0] in request.form:
                self.categories.checked.append(i[0])

        if not FlaskForm.validate(self):
            return False
        for i in self.images.data:
            if i.filename and not allowed_file(i.filename, Image.get_extensions()):
                self.images.errors.append('Incorrect image format')
                return False
        if self.file.data and not allowed_file(self.file.data.filename, ProblemTests.get_extensions()):
            self.file.errors.append('Incorrect zip archive format')
            return False
        if self.file.data and not TestProgram.check_tests_zip(deepcopy(self.file.data.stream).read()):
            self.file.errors.append('Incorrect zip archive format')
            return False

        examples = self.examples.data.strip().split(self.example_split_tag)
        for i in examples:
            if not self.examples.data.strip():
                break
            ex_data = [j.strip() for j in i.strip().split(self.example_data_tag)]
            if len(ex_data) != 2:
                self.examples.errors.append('Incorrect examples format')
                return False
        return True

