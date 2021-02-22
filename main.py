from flask import Flask, render_template, request, redirect, abort
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, \
    BooleanField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired
import os
import threading
from db_data import db_session
from db_data.problem import Problem
from db_data.solution import Solution
from program_testing.prog_lang import languages

from program_testing.test_program import TestProgram, TestResult


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class SendForm(FlaskForm):
    text = TextAreaField('Input source code here', validators=[])
    file = FileField('Select file', validators=[])
    select = SelectField('Select programming language')
    submit = SubmitField('Send')


DB_PT = os.path.abspath('db/program_testing.db')
SECRET_KEY = 'secret_key'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


def send_solution(source, lang, db_sess):
    solution = Solution()
    solution.problem_id = 2
    solution.lang_code_name = lang
    db_sess.add(solution)
    db_sess.commit()
    test_program.add_solution(source, solution.id)
    test_program.add_to_queue(db_sess, solution)
    return solution.id


@app.errorhandler(404)
def error404(error):
    return render_template('error404.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    correct = True
    if form.validate_on_submit():
        return redirect('/success')

    return render_template('login.html', form=form, correct=correct)


@app.route('/send', methods=['GET', 'POST'])
def send():
    db_sess = db_session.create_session()
    form = SendForm()
    form.select.choices = [(k, v.name) for k, v in languages.items()]

    if form.validate_on_submit():
        source = form.file.data.stream.read().decode()
        if not source:
            source = form.text.data
            form.text.data = ''
        if source:
            id = send_solution(source, form.select.data, db_sess)
            return redirect(f'dynamic/{id}')

    return render_template('send.html', form=form)


@app.route('/dynamic/<int:solution_id>', methods=['GET', 'POST'])
def dynamic(solution_id):
    db_sess = db_session.create_session()
    solution = test_program.read_solution(db_sess, solution_id)
    if not solution:
        abort(404)
    return render_template('dynamic.html', solution_id=solution_id,
                           update_timeout=0.5, default_text='')


@app.route('/update')
def update():
    db_sess = db_session.create_session()

    solution_id = request.args.get('solution_id', default=None, type=int)
    if solution_id is None:
        return ''
    solution = test_program.read_solution(db_sess, solution_id)
    if not solution:
        return ''
    data = request.args.get('secret_data')
    text = solution.state
    if solution.completed:
        text = solution.verdict
        if data and text in data:
            text = None
        else:
            print('Result tests')
            test_results = test_program.read_test_results(solution)
            for n, i in enumerate(test_results):
                i: TestResult
                print(n + 1, i.time, i.memory, i.stdout, i.stderr)
            ...

    return render_template('update.html', text=text)


if __name__ == '__main__':
    db_session.global_init(app.config['DB_PT'])

    test_program = TestProgram()
    thread = threading.Thread(target=test_program.start, args=())
    thread.daemon = True
    thread.start()

    # solution = Solution()
    # solution.problem_id = 1
    # solution.lang_code_name = 'c++'
    # session.add(solution)
    # session.commit()
    #
    # p = Problem()
    # p.memory_limit = 2**20*45
    # p.time_limit=1
    # session.add(p)
    # session.commit()

    # solution = Solution()
    # solution.problem_id = 2
    # solution.lang_code_name = 'python'
    # session.add(solution)
    # session.commit()
    #
    # p = Problem()
    # p.memory_limit = 2 ** 20 * 45
    # p.time_limit = 3
    # session.add(p)
    # session.commit()

    app.run()
