from flask import render_template, redirect, flash, request
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from data import db_session
from data.user import User
from forms.login import LoginForm

from global_app import get_app

app = get_app()


@app.route('/select_users', methods=['GET'])
@login_required
def select_user():
    db_sess = db_session.create_session()
    username = request.args.get('username', default='', type=str)
    _return = request.args.get('return', default='', type=str)
    user_ids = request.args.get('user_ids', default='', type=str)
    _user_ids = user_ids
    try:
        _user_ids = _user_ids.split(',') if _user_ids else []
        _user_ids = list(map(int, _user_ids))
    except ValueError:
        abort(404)
    selected_users = db_sess.query(User).filter(User.id.in_(_user_ids)).all()
    if len(selected_users) != len(_user_ids):
        abort(404)
    if not _return:
        abort(404)

    users = []
    if username:
        users = db_sess.query(User).filter(User.username.like(f'%{username}%')).\
            filter(User.id.notin_(_user_ids)).all()
    return render_template('select_users.html', **locals())
