import argparse
import json
import time

import os
import threading
import socket

from data import db_session
from data.problem_category import ProblemCategory
from data.user import User
import program_testing.prog_lang as prog_lang
import global_app
from program_testing import test_program as tp
from program_testing.create_process import init_user
from program_testing.test_program import TestProgram
from utils.init_db import init_db
from utils.send_mail import test_email

directory = os.path.dirname(__file__)
SECRET_KEY = 'teststem_sect_kelkzdt,356h356h356h'
MAIL_CONFIRM_SECRET_KEY = 'test_m_conf_sec_key_lkzdtrhryyerbn,'
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_LOGIN = ...
MAIL_PASSWORD = ...
DB_PT = os.path.join(directory, 'db/test_system.db')
CONFIG_LANG = os.path.join(directory, 'config/test_program.json')
UPDATE_STATUS_TIMEOUT = 0.5
TEST_THREADS = 1

global_app.global_init(__name__, directory)
app = global_app.get_app()
app.config.from_object(__name__)
current_user: User


def init_account():
    print('Init account...')
    db_session.global_init(app.config['DB_PT'])
    db_sess = db_session.create_session()
    if os.path.exists('admin.txt'):
        with open('admin.txt', encoding='utf8') as f:
            line = f.read().strip().split()
            if len(line) > 1:
                user = User()
                user.username = line[0]
                user.confirmed_email = True
                user.type = 10
                user.set_password(line[1])
                db_sess.add(user)
                db_sess.commit()
    if os.path.exists('teacher.txt'):
        with open('teacher.txt', encoding='utf8') as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                line = line.strip().split()
                if len(line) > 1:
                    user = User()
                    user.username = line[0]
                    user.confirmed_email = True
                    user.type = 20
                    user.set_password(line[1])
                    db_sess.add(user)
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
import components.register
import components.profile
import components.categories


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init_user', action='store_true')
    parser.add_argument('--account', action='store_true')
    args = parser.parse_args()

    with open(app.config['CONFIG_LANG'], 'r') as f:
        data = json.load(f)
    prog_lang.init(data)
    app.config['MAIL_LOGIN'] = data['mail_login']
    app.config['MAIL_PASSWORD'] = data['mail_password']
    test_email()
    if args.init_user:
        init_user(data['run_as_user_linux'])
        exit()

    tp.init(data)

    if args.account:
        init_account()
    db_session.global_init(app.config['DB_PT'])
    init_db()

    test_program: TestProgram = tp.get_test_program()
    thread = threading.Thread(target=test_program.start, args=(),
                              kwargs={'threads': app.config['TEST_THREADS']})

    thread.daemon = True
    thread.start()
    time.sleep(0.1)


def main():
    h_name = socket.gethostname()
    ip_address = socket.gethostbyname(h_name)
    print('Local ip:', ip_address)

    port = int(os.environ.get('PORT', 8080))
    app.run(host='localhost', port=port)


init()
if __name__ == '__main__':
    main()
