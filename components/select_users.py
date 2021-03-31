from flask import render_template, redirect, flash, request
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from data import db_session
from data.user import User
from forms.login import LoginForm
from forms.search_user import SearchUserForm

from global_app import get_app
from utils.utils import get_message_from_form

app = get_app()


@app.route('/select_users', methods=['GET', 'POST'])
@login_required
def select_user():
    db_sess = db_session.create_session()
    form = SearchUserForm()
    search = request.args.get('search', default='', type=str)
    _return = request.args.get('return', default='', type=str)
    user_ids = request.args.get('user_ids', default='', type=str)
    _user_ids = user_ids
    try:
        _user_ids = _user_ids.split(',') if _user_ids else []
        _user_ids = list(map(int, _user_ids))
    except ValueError:
        abort(404)
    selected_search_objects = db_sess.query(User).filter(User.id.in_(_user_ids)).all()
    if len(selected_search_objects) != len(_user_ids):
        abort(404)
    if not _return:
        abort(404)

    search_objects = []
    search_field = ''
    if form.is_submitted():
        search = ''
    if form.validate_on_submit() or search:
        if not form.validate_on_submit():
            form.search.data = search
        search_field = form.search.data.strip()
        search_objects = db_sess.query(User).filter(User.username.like(f'%{search_field}%')). \
            filter(User.id.notin_(_user_ids)).all()
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('select_users.html', **locals())
