from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import TimeField
from wtforms.validators import DataRequired, InputRequired

from forms.utils.multiply_checkbox_field import MultiplyCheckboxField
from utils.utils import get_duration_from_time


class SubmitSessionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[])
    problems = MultiplyCheckboxField('problem_checkbox', 'Problems')
    # time = TimeField('Duration (HH:MM:SS)', validators=[DataRequired()],
    #                  format='%H:%M:%S', render_kw={'step': '1'})
    time = TimeField('Duration (HH:MM)', validators=[DataRequired()],
                     format='%H:%M')
    submit = SubmitField('Add')

    def validate(self):
        self.problems.checked = []
        for i in self.problems.choices:
            if self.problems.prefix_id + i[0] in request.form:
                self.problems.checked.append(i[0])

        if not FlaskForm.validate(self):
            return False

        if not self.problems.checked:
            self.problems.errors.append('At least one task should be selected')
            return False

        if get_duration_from_time(self.time.data).total_seconds() < 60:
            self.time.errors.append('Duration must be at least 1 minute')
            return False

        return True
