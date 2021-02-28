import json
import shutil

from flask import Markup, url_for
from flask import Flask, render_template, request, redirect, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import threading
from data import db_session
from data.problem import Problem
from data.solution import Solution
from data.user import User
from forms.login import LoginForm
from forms.submit_problem import SubmitProblemForm
from forms.submit_solution import SubmitSolutionForm
from program_testing.message import get_message_solution
import program_testing.prog_lang as prog_lang
import program_testing.test_program as test_program
from program_testing.test_program import TestProgram, TestResult

SECRET_KEY = 'test_system_secret_key'
DEBUG = False
DB_PT = os.path.abspath('db/test_system.db')
CONFIG_LANG = os.path.abspath('config/test_program.json')

app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


recreate_db = True

if recreate_db:
    if os.path.exists(DB_PT):
        os.remove(DB_PT)
    db_session.global_init(DB_PT)
    db_sess = db_session.create_session()
    p = Problem()
    p.name = 'пятая задача с городской олимпиады'
    p.memory_limit = 2 ** 20 * 512
    p.time_limit = 5
    db_sess.add(p)

    p = Problem()
    p.name = 'A + B'
    p.memory_limit = 2 ** 20 * 32
    p.time_limit = 5
    db_sess.add(p)

    user = User()
    user.username = 'qwqwqwqwqw'
    user.set_password('1qwqwwq23')
    db_sess.add(user)

    user = User()
    user.username = 'admin'
    user.set_password('admin')
    db_sess.add(user)

    user = User()
    user.username = 'user'
    user.set_password('user')
    db_sess.add(user)

    solution = Solution()
    solution.user_id = 1
    solution.problem_id = 1
    solution.lang_code_name = 'c++'
    db_sess.add(solution)

    solution = Solution()
    solution.user_id = 1
    solution.problem_id = 2
    solution.lang_code_name = 'python'
    db_sess.add(solution)

    db_sess.commit()

    print('Clear solution folder')
    folder = os.path.join('program_testing', 'solution')
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def send_solution(problem_id, source, lang, db_sess):
    solution = Solution()
    solution.user_id = current_user.id
    solution.problem_id = problem_id
    solution.lang_code_name = lang
    db_sess.add(solution)
    db_sess.commit()
    test_program.add_solution(source, solution.id)
    test_program.add_to_queue(db_sess, solution)
    return solution


def get_solution_row(solution):
    i = solution
    solution_row = [x if type(
        x) == tuple else (x, '') for x in [
                        i.id, i.sent_date.strftime("%d %B %Y, %I:%M%p"), languages[i.lang_code_name].name,
                        get_message_solution(i),
                        i.max_time, f'{i.max_memory // 1024} Kb'
                    ]]
    return solution_row


def get_message_from_form(form):
    for i in form.__dict__.values():
        if hasattr(i, 'errors'):
            if i.errors:
                msg = f'{i.label.text}: {i.errors[0]}'
                return msg
    return ''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def error404(error):
    return render_template('error.html', code=404), 404


@app.errorhandler(401)
def error401(error):
    return redirect('/login')


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               message='Incorrect username or password',
                               form=form)
    return render_template('login.html', form=form)


@app.route('/problemset', methods=['GET', 'POST'])
@login_required
def problemset():
    db_sess = db_session.create_session()
    return render_template('problemset.html', problem=db_sess.query(Problem).all())


@app.route('/add_problem', methods=['GET', 'POST'])
@login_required
def add_problem():
    db_sess = db_session.create_session()
    form = SubmitProblemForm()

    if form.validate_on_submit():
        problem = Problem()
        problem.name = form.name.data
        problem.time_limit = form.time.data / 1000
        problem.memory_limit = form.memory.data * 1024
        db_sess.add(problem)
        db_sess.commit()
        test_program.add_problem(
            problem.id, form.file.data.stream.read(), form.task_text.data)
        return redirect(url_for('problemset'))

    msg = get_message_from_form(form)

    return render_template('add_problem.html', form=form, message=msg)


@app.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
@login_required
def submit(problem_id):
    db_sess = db_session.create_session()

    problem = db_sess.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        abort(404)

    form = SubmitSolutionForm()

    form.select.choices = [(k, v.name) for k, v in languages.items()]

    if form.validate_on_submit():
        if form.file.data:
            source = form.file.data.stream.read()
        elif form.text.data:
            source = form.text.data.encode()
        else:
            return render_template('submit.html', form=form,
                                   problem=problem, message='Select file or input source code')
        solution = send_solution(problem_id, source, form.select.data, db_sess)
        return redirect('/status')

    return render_template('submit.html', form=form,
                           problem=problem)


@app.route('/status')
@login_required
def status():
    db_sess = db_session.create_session()
    solution = sorted(current_user.solution, key=lambda x: x.sent_date, reverse=True)
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    return render_template('status.html', solution_rows=solution_rows,
                           rows_to_update=rows_to_update,
                           update_timeout=0.5)


@app.route('/update')
@login_required
def update():
    db_sess = db_session.create_session()

    solution_ids = request.args.get('rows_to_update', default=None, type=str)
    if solution_ids is None:
        return ''
    solution_ids = json.loads(solution_ids)

    solution = db_sess.query(Solution).filter(Solution.id.in_(
        solution_ids)).order_by(Solution.id).all()
    if not solution or len(solution) != len(solution_ids):
        return ''

    solution_rows = {i.id: [render_template('status_row.html',
                                            row=get_solution_row(i)),
                            i.completed] for i in solution}
    for i in solution:
        if i.completed:
            test_res = test_program.read_test_results(i)
            for j in test_res:
                j: TestResult
                print(j.time, j.memory, j.stdout, j.stderr)

    return json.dumps(solution_rows)


if __name__ == '__main__':
    with open(app.config['CONFIG_LANG'], 'r') as f:
        data = json.load(f)
    prog_lang.init(data)
    test_program.init(data)

    languages = prog_lang.get_languages()

    db_session.global_init(app.config['DB_PT'])

    test_program = TestProgram()
    thread = threading.Thread(target=test_program.start, args=(),
                              kwargs={'threads': 3})
    thread.daemon = True
    thread.start()

    app.run(port=80, host='localhost')
