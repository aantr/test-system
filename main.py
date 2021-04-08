import json
from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_required, current_user
import os
import threading

from data import db_session
from data.problem import Problem
from data.problem_category import ProblemCategory
from data.problem_tests import ProblemTests
from data.task import Task
from data.user import User
import program_testing.prog_lang as prog_lang
import global_app
from program_testing import test_program as tp
from utils.init_db import init_db

SECRET_KEY = 'test_system_secret_key'
DB_PT = os.path.abspath('db/test_system.db')
CONFIG_LANG = os.path.abspath('config/test_program.json')
UPDATE_STATUS_TIMEOUT = 0.5
TEST_THREADS = 3

global_app.global_init(__name__)
app = global_app.get_app()
app.config.from_object(__name__)
current_user: User

recreate_db = 0

def on_recreate_db():
    print('Recreate db...')
    if os.path.exists(DB_PT):
        os.remove(DB_PT)

    db_sess = db_session.create_session()

    p = Problem()
    p.name = 'A + B'
    p.memory_limit = 2 ** 20 * 32
    p.time_limit = 3
    p.task = Task()
    p.problem_tests = ProblemTests()
    db_sess.add(p)

    user = User()
    user.username = 'admin'
    user.type = 10
    user.set_password('admin')
    db_sess.add(user)

    user = User()
    user.username = 'teacher'
    user.type = 20
    user.set_password('teacher')
    db_sess.add(user)

    user = User()
    user.username = 'student'
    user.type = 30
    user.set_password('student')
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

# Components
import components.action_link
import components.groups
import components.invite
import components.login
import components.problem
import components.session
import components.solution
import components.workplace
import components.select_users
import components.select_group
import components.errors
import components.index
import components.system_state


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'img/favicon.ico')


if __name__ == '__main__':
    with open(app.config['CONFIG_LANG'], 'r') as f:
        data = json.load(f)
    prog_lang.init(data)
    tp.init(data)

    languages = prog_lang.get_languages()

    db_session.global_init(app.config['DB_PT'])
    init_db()
    if recreate_db:
        on_recreate_db()

    test_program = tp.get_test_program()
    thread = threading.Thread(target=test_program.start, args=(),

                              kwargs={'threads': app.config['TEST_THREADS']})

    thread.daemon = True
    thread.start()

    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
