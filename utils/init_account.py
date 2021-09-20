import os

import global_app
from data import db_session
from data.user import User

app = global_app.get_app()


def init_account():
    print('Init account...')
    db_session.global_init(app.config['DB_PT'])
    db_sess = db_session.create_session()
    if os.path.exists('admin.txt'):
        with open('admin.txt', encoding='utf8') as f:
            line = f.read().strip().split()
            if len(line) > 1:
                user = db_sess.query(User).filter(User.username == line[0]).first()
                if not user:
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
                    user = db_sess.query(User).filter(User.username == line[0]).first()
                    if not user:
                        user = User()
                        user.username = line[0]
                    user.confirmed_email = True
                    user.type = 20
                    user.set_password(line[1])
                    db_sess.add(user)
                    db_sess.commit()
