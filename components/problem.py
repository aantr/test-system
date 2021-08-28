import os
import shutil

from flask import request, send_from_directory

from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from wtforms.validators import DataRequired

from data.solution import Solution
from forms.edit_problem import EditProblemForm
from global_app import get_app, get_dir
from program_testing import test_program as tp

from data import db_session
from data.image import Image
from data.problem import Problem
from data.problem_category import ProblemCategory
from data.problem_tests import ProblemTests
from forms.submit_problem import SubmitProblemForm
from utils.permissions_required import student_required, teacher_required
from utils.utils import get_message_from_form

app = get_app()


@app.route('/add_problem', methods=['GET', 'POST'])
@teacher_required
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
        problem.user_id = current_user.id
        problem.examples = form.examples.data
        problem.input_text = form.input_text.data
        problem.output_text = form.output_text.data
        problem.note = form.note.data
        problem.task_text = form.task_text.data
        problem.display_problemset = form.display_problemset.data

        for i in form.categories.checked:
            problem.categories.append(categories[i])
        db_sess.add(problem)
        db_sess.flush()

        ids = []
        for i in sorted(form.images.data, key=lambda x: x.filename):
            images_extensions = Image.get_extensions()
            if not i.filename or len(i.filename) <= 1 or \
                    os.path.splitext(i.filename)[1][1:] \
                    not in images_extensions:
                continue
            image = Image()
            image.extension = os.path.splitext(i.filename)[1][1:]
            db_sess.add(image)
            db_sess.flush()
            ids.append(image.id)

            with open(os.path.join(get_dir(), 'static', 'files', 'images',
                                   image.get_name()), 'wb') as f:
                f.write(i.stream.read())
        problem.images_ids = ','.join(map(str, ids))
        test_program.add_problem(problem, form.file.data.stream.read())
        flash(f'Successfully added problem "{problem.name}"', category='success')
        db_sess.commit()
        return redirect(url_for('add_problem'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('add_problem.html', **locals())


@app.route('/edit_problem/<int:id>', methods=['GET', 'POST'])
@teacher_required
def edit_problem(id):
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.id == id).first()
    if not problem:
        abort(404)
    if problem.user_id != current_user.id:
        abort(403)
    args = ['name', 'task_text', 'input_text',
            'output_text', 'examples', 'note', 'display_problemset']
    form = EditProblemForm(
        time=problem.time_limit * 1000,
        memory=problem.memory_limit // 1024,
        **{i: problem.__getattribute__(i) for i in args}
    )
    for i in problem.categories:
        form.categories.checked.append(str(i.id))
    categories = {str(i.id): i for i in db_sess.query(ProblemCategory).all()}
    form.categories.choices = [(str(k), v.name) for k, v in categories.items()]

    test_program = tp.get_test_program()
    if form.validate_on_submit():
        problem.name = form.name.data
        problem.time_limit = form.time.data / 1000
        problem.memory_limit = form.memory.data * 1024
        problem.examples = form.examples.data
        problem.input_text = form.input_text.data
        problem.output_text = form.output_text.data
        problem.note = form.note.data
        problem.task_text = form.task_text.data
        problem.display_problemset = form.display_problemset.data

        problem.categories.clear()
        for i in form.categories.checked:
            problem.categories.append(categories[i])
        db_sess.flush()

        if form.file.data:
            dir_tests = os.path.join(get_dir(), 'files', 'tests', f'{problem.problem_tests.id}')
            shutil.rmtree(dir_tests, ignore_errors=True)
            db_sess.delete(problem.problem_tests)
            problem.problem_tests = ProblemTests()
            db_sess.flush()
            test_program.add_problem(problem, form.file.data.stream.read())
        if form.images.data and form.images.data[0]:
            if problem.images_ids:
                ids = list(map(int, problem.images_ids.split(',')))
            else:
                ids = []
            images = db_sess.query(Image).filter(Image.id.in_(ids)).all()
            for i in images:
                os.remove(os.path.join(get_dir(), 'static', 'files', 'images',
                                       i.get_name()))
                db_sess.delete(i)
            ids = []
            for i in sorted(form.images.data, key=lambda x: x.filename):
                images_extensions = Image.get_extensions()
                if not i.filename or len(i.filename) <= 1 or \
                        os.path.splitext(i.filename)[1][1:] \
                        not in images_extensions:
                    continue
                image = Image()
                image.extension = os.path.splitext(i.filename)[1][1:]
                db_sess.add(image)
                db_sess.flush()
                ids.append(image.id)
                with open(os.path.join(get_dir(), 'static', 'files', 'images',
                                       image.get_name()), 'wb') as f:
                    f.write(i.stream.read())
            problem.images_ids = ','.join(map(str, ids))

        flash(f'Successfully edited problem "{problem.name}"', category='success')
        db_sess.commit()
        return redirect(url_for('get_problem', id=problem.id))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('edit_problem.html', **locals())


@app.route('/problem/<int:id>')
@student_required
def get_problem(id):
    test_program = tp.get_test_program()
    args = request.args
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.id == id).first()
    if not problem:
        abort(404)
    if not problem.display_problemset and problem.user_id != current_user.id:
        abort(403)
    if problem.images_ids:
        ids = list(map(int, problem.images_ids.split(',')))
    else:
        ids = []
    images = db_sess.query(Image).filter(Image.id.in_(ids))
    images_path = []
    base = url_for('static', filename=f'files/images/')
    for image in images:
        images_path.append(f'{base}{image.id}.{image.extension}')
    examples = []
    for i in problem.examples.split(SubmitProblemForm.example_split_tag):
        ex_data = [j.strip('\n') for j in i.strip('\n').split(SubmitProblemForm.example_data_tag)]
        examples.append(ex_data)
    if not problem.examples:
        examples = []
    categories = [i.name for i in problem.categories]
    categories = ', '.join(categories)
    task = render_template('task.html',
                           task_text=problem.task_text,
                           note=problem.note,
                           images=images_path,
                           examples=examples,
                           input_text=problem.input_text,
                           output_text=problem.output_text,
                           categories=categories)
    edit = problem.user_id == current_user.id
    success_solution = db_sess.query(Solution).filter(Solution.problem_id == id). \
        filter(Solution.user_id == current_user.id).filter(Solution.success == 1). \
        filter(Solution.session_id == args.get('session_id')).first()
    return render_template('problem.html', **locals())


@app.route('/download_problem_images/<int:id>', methods=['GET'])
@teacher_required
def download_problem_images(id):
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.id == id).first()
    if not problem:
        abort(404)
    if problem.user_id != current_user.id:
        abort(403)
    if problem.images_ids:
        ids = list(map(int, problem.images_ids.split(',')))
    else:
        ids = []
    images = db_sess.query(Image).filter(Image.id.in_(ids))
    images_path = []
    base = os.path.join(get_dir(), 'static', 'files', 'images')
    for image in images:
        images_path.append(os.path.join(base, image.get_name()))
    filename = f'temp_{problem.id}'
    base = os.path.join(get_dir(), 'files', 'temp')
    if not os.path.exists(os.path.join(base, filename)):
        os.mkdir(os.path.join(base, filename))
    for i in images_path:
        shutil.copyfile(i, os.path.join(base, filename, os.path.split(i)[1]))
    shutil.make_archive(os.path.join(base, filename), 'zip', os.path.join(base, filename))
    shutil.rmtree(os.path.join(base, filename))
    return send_from_directory(
        directory=base, filename=f'{filename}.zip',
        as_attachment=True, attachment_filename=f'images_{problem.id}.zip')


@app.route('/download_problem_tests/<int:id>', methods=['GET'])
@teacher_required
def download_problem_tests(id):
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.id == id).first()
    if not problem:
        abort(404)
    if problem.user_id != current_user.id:
        abort(403)
    filename = f'temp_{problem.id}'
    base = os.path.join(get_dir(), 'files', 'temp')
    shutil.make_archive(os.path.join(base, filename), 'zip',
                        os.path.join(get_dir(), 'files', 'tests',
                                     str(problem.problem_tests_id)))
    return send_from_directory(
        directory=base, filename=f'{filename}.zip',
        as_attachment=True, attachment_filename=f'tests_{problem.id}.zip')


@app.route('/problemset/<int:id>', methods=['GET'])
@student_required
def problemset_category(id):
    db_sess = db_session.create_session()
    category: ProblemCategory = db_sess.query(ProblemCategory). \
        filter(ProblemCategory.id == id).first()
    if not category:
        abort(404)
    problem = db_sess.query(Problem).filter(Problem.display_problemset == 1) \
        .filter(Problem.categories.any(id=id)).all()
    name = category.name
    return render_template('problemset.html', **locals())


@app.route('/problemset/all', methods=['GET'])
@student_required
def problemset_all():
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.display_problemset == 1).all()
    name = 'All problems'
    return render_template('problemset.html', **locals())


@app.route('/problemset', methods=['GET'])
@student_required
def problemset():
    db_sess = db_session.create_session()
    categories = db_sess.query(ProblemCategory).all()
    categories = [{'name': 'All', 'id': 'all'}] + categories
    return render_template('problem_categories.html', **locals())


@app.route('/my_problems', methods=['GET'])
@teacher_required
def my_problems():
    db_sess = db_session.create_session()
    problem = db_sess.query(Problem).filter(Problem.user_id == current_user.id).all()
    return render_template('my_problems.html', **locals())
