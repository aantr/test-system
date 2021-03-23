import os

from flask import Blueprint, request

from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from program_testing import test_program as tp

from data import db_session
from data.image import Image
from data.problem import Problem
from data.problem_category import ProblemCategory
from data.problem_tests import ProblemTests
from data.task import Task
from forms.submit_problem import SubmitProblemForm
from utils import get_message_from_form

problem = Blueprint('problem', __name__,
                    template_folder='templates',
                    static_folder='static')


@problem.route('/add_problem', methods=['GET', 'POST'])
@login_required
def add_problem():
    db_sess = db_session.create_session()
    form = SubmitProblemForm()
    test_program = tp.get_test_program()

    categories = {str(i.id): i for i in db_sess.query(ProblemCategory).all()}
    form.categories.choices = [(str(k), v.name) for k, v in categories.items()]

    if form.validate_on_submit():

        problem = Problem()
        problem.name = form.name.data
        problem.time_limit = form.time.data / 1000
        problem.memory_limit = form.memory.data * 1024
        problem.problem_tests = ProblemTests()
        problem.task = Task()
        problem.user.id = current_user.id
        db_sess.add(problem)
        db_sess.flush()

        for i in form.categories.checked:
            problem.categories.append(categories[i])

        images = []
        for i in sorted(form.images.data, key=lambda x: x.filename):
            images_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            if not i.filename or len(i.filename) <= 1 or os.path.splitext(i.filename)[1][1:] \
                    not in images_extensions:
                continue
            base = url_for('static', filename=f'files/images/')
            image = Image()
            image.extension = os.path.splitext(i.filename)[1][1:]
            db_sess.add(image)
            db_sess.flush()
            images.append(f'{base}{image.id}.{image.extension}')

            with open(os.path.join('static', 'files', 'images',
                                   f'{image.id}.{image.extension}'), 'wb') as f:
                f.write(i.stream.read())

        task_text = form.task_text.data.strip().replace('\n', '')
        note = form.note.data.strip().replace('\n', '')
        input_text = form.input_text.data.strip().replace('\n', '')
        output_text = form.output_text.data.strip().replace('\n', '')

        examples = []
        for i in form.examples.data.strip().split(form.example_split_tag):
            ex_data = [j.strip('\n') for j in i.strip('\n').split(form.example_data_tag)]
            examples.append(ex_data)

        template = render_template('task.html',
                                   task_text=task_text,
                                   note=note,
                                   images=images,
                                   examples=examples,
                                   input_text=input_text,
                                   output_text=output_text)

        test_program.add_problem(
            problem, form.file.data.stream.read(), template)
        flash(f'Successfully added problem "{problem.name}"', category='success')
        db_sess.commit()
        return redirect(url_for('problem.add_problem'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_problem.html', form=form)


@problem.route('/problem/<int:problem_id>')
@login_required
def get_problem(problem_id):
    test_program = tp.get_test_program()
    args = request.args

    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        abort(404)
    task = test_program.read_problem_task(problem)

    return render_template('problem.html', **locals())


@problem.route('/problemset', methods=['GET', 'POST'])
@login_required
def problemset():
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).all()
    return render_template('problemset.html', **locals())
