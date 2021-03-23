import json
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required
import os
import threading

from data import db_session
from data.problem import Problem
from data.problem_category import ProblemCategory
from data.problem_tests import ProblemTests
from data.task import Task
from data.user import User
import program_testing.prog_lang as prog_lang
from program_testing import test_program as tp
from blueprint.session.session import session_bp
from blueprint.problem.problem import problem
from blueprint.solution.solution import solution
from blueprint.login.login import login
from blueprint.action_link.action_link import action_bp, clear_all_actions
from blueprint.workplace.workplace import workplace_bp

SECRET_KEY = 'test_system_secret_key'
DEBUG = False
DB_PT = os.path.abspath('db/test_system.db')
CONFIG_LANG = os.path.abspath('config/test_program.json')
UPDATE_STATUS_TIMEOUT = 0.5
TEST_THREADS = 3

app = Flask(__name__)
app.config.from_object(__name__)

app.register_blueprint(session_bp)
app.register_blueprint(problem)
app.register_blueprint(solution)
app.register_blueprint(login)
app.register_blueprint(action_bp)
app.register_blueprint(workplace_bp)

login_manager = LoginManager()
login_manager.init_app(app)
current_user: User

recreate_db = 0

if recreate_db:
    if os.path.exists(DB_PT):
        os.remove(DB_PT)
    db_session.global_init(DB_PT)
    db_sess = db_session.create_session()

    p = Problem()
    p.name = 'A + B'
    p.memory_limit = 2 ** 20 * 32
    p.time_limit = 1
    p.task = Task()
    p.problem_tests = ProblemTests()
    db_sess.add(p)

    user = User()
    user.username = 'u1'
    user.set_password('1234')
    db_sess.add(user)

    user = User()
    user.username = 'admin'
    user.set_password('admin')
    db_sess.add(user)

    user = User()
    user.username = 'user'
    user.set_password('user')
    db_sess.add(user)

    cat = ProblemCategory()
    cat.name = 'Массивы'
    db_sess.add(cat)

    cat = ProblemCategory()
    cat.name = 'Функции'
    db_sess.add(cat)

    cat = ProblemCategory()
    cat.name = 'Циклы'
    db_sess.add(cat)

    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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


@app.route('/server_state')
@login_required
def server_state():
    queue = test_program.get_queue_length()
    threads = app.config['TEST_THREADS']
    return render_template('server_state.html',
                           queue=queue, threads=threads)


if __name__ == '__main__':
    with open(app.config['CONFIG_LANG'], 'r') as f:
        data = json.load(f)
    prog_lang.init(data)
    tp.init(data)

    languages = prog_lang.get_languages()

    db_session.global_init(app.config['DB_PT'])
    clear_all_actions()

    test_program = tp.get_test_program()
    thread = threading.Thread(target=test_program.start, args=(),
                              kwargs={'threads': app.config['TEST_THREADS']})
    thread.daemon = True
    thread.start()

    app.run(port=80, host='localhost')
