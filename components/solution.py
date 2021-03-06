import json

from flask import Markup, url_for, flash, current_app
from flask import render_template, request, \
    redirect, abort
from flask_login import current_user
from data.session import Session
from data.user import User
from global_app import get_app

from data import db_session
from data.problem import Problem

from data.solution import Solution
from forms.submit_solution import SubmitSolutionForm
from program_testing import prog_lang
from program_testing.message import get_message_solution
from program_testing.prog_lang import get_languages
from program_testing.test_program import TestProgram
from utils.permissions_required import student_required
from utils.send_solution import send_solution
from utils.utils import get_session_joined, get_message_from_form
from utils.solution_row import get_solution_row

app = get_app()
current_user: User


@app.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
@student_required
def submit(problem_id):
    languages = prog_lang.get_languages()
    db_sess = db_session.create_session()

    problem = db_sess.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        abort(404)

    form = SubmitSolutionForm()
    form.select.choices = [(k, v.name) for k, v in languages.items()]

    from_problemset = request.args.get('problemset', default=False, type=bool)
    from_session_id = request.args.get('session_id', default=None, type=int)
    session = get_session_joined(db_sess)
    session: Session
    session_id = None
    if not from_problemset and session and \
            (session.started or session.user_id == current_user.id):
        problems_ids = [i.id for i in session.problems]
        if problem_id in problems_ids:
            session_id = session.id
    available = True
    if session and session_id is None and from_session_id is not None and \
            session.user_id != current_user.id:
        available = False
    if session and session_id is not None and from_session_id is not None \
            and from_session_id != session_id and \
            session.user_id != current_user.id:
        available = False

    # if from_session_id != session_id:
    #     session_id = None

    if not available:
        return redirect(url_for('workplace_info'))

    if form.validate_on_submit():
        if form.file.data:
            source = form.file.data.stream.read()
        elif form.text.data:
            source = form.text.data.encode()
        else:
            flash('Select file or input source code', category='danger')
            return render_template('submit.html', form=form, problem=problem)

        solution = send_solution(problem_id, source, form.select.data, session_id, current_user, db_sess)
        if session_id:
            return redirect(url_for('workplace_status'))
        return redirect('/status')
    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')

    return render_template('submit.html', **locals())


@app.route('/status')
@student_required
def status():
    db_sess = db_session.create_session()
    solution = db_sess.query(Solution).filter(Solution.user_id == current_user.id). \
        filter(Solution.session_id == None).order_by(Solution.sent_date.desc()).limit(100).all()
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    update_timeout = current_app.config['UPDATE_STATUS_TIMEOUT']
    status_base = render_template('status_base.html', **locals())
    return render_template('status.html', **locals())


@app.route('/all_submits')
@student_required
def all_submits():
    db_sess = db_session.create_session()
    solution = db_sess.query(Solution). \
        filter(Solution.session_id == None).order_by(Solution.sent_date.desc()).limit(100).all()
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    update_timeout = current_app.config['UPDATE_STATUS_TIMEOUT']
    status_base = render_template('status_base.html', **locals())
    return render_template('all_submits.html', **locals())


@app.route('/update')
@student_required
def update():
    db_sess = db_session.create_session()
    solution_ids = request.args.get('rows_to_update', default=None, type=str)
    if solution_ids is None:
        return ''
    solution_ids = json.loads(solution_ids)
    solution = db_sess.query(Solution).filter(Solution.id.in_(
        solution_ids)).all()
    if not solution or len(solution) != len(solution_ids):
        return ''
    solution_rows = {i.id: [render_template('status_row.html',
                                            row=get_solution_row(i)),
                            i.completed] for i in solution}
    return json.dumps(solution_rows)


@app.route('/solution/<int:solution_id>')
@student_required
def get_solution(solution_id):
    db_sess = db_session.create_session()
    solution = db_sess.query(Solution).filter(Solution.id == solution_id).first()
    if not solution:
        abort(404)
    if solution.user_id != current_user.id and not current_user.has_rights_teacher():
        abort(403)
    try:
        source = TestProgram.read_source_code(solution)
    except UnicodeDecodeError:
        source = 'Failed to load source code'
    lang = get_languages()[solution.lang_code_name].name
    max_sym = 5000
    if solution.completed:
        tests = TestProgram.read_tests(solution.problem)
        test_results = TestProgram.read_test_results(solution)
        tests_success = len(test_results)
        message_solution = get_message_solution(solution)
        if not solution.success:
            tests_success -= 1
            if current_user.has_rights_teacher():
                stdin, correct = tests[len(test_results) - 1]
                stdin = stdin[:max_sym]
                correct = correct[:max_sym]
                stdout = test_results[-1].stdout
                stderr = test_results[-1].stderr
                if stdout:
                    stdout = stdout[:max_sym]
                if stderr:
                    stderr = stderr[:max_sym]

    return render_template('solution.html', **locals())
