from flask import render_template, redirect, flash, request
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from data import db_session
from data.group import Group, GroupMember
from data.session import SessionMember
from data.user import User
from forms.login import LoginForm
from forms.search_user import SearchUserForm

from global_app import get_app
from utils.permissions_required import student_required
from utils.utils import get_message_from_form

app = get_app()


@app.route('/select_users', methods=['GET', 'POST'])
@student_required
def select_user():
    db_sess = db_session.create_session()
    form = SearchUserForm()
    search = request.args.get('search', default='', type=str)
    _return = request.args.get('return', default='', type=str)
    user_ids = request.args.get('user_ids', default='', type=str)
    _user_ids = user_ids
    group_id = request.args.get('group_id', default='', type=int)
    session_id = request.args.get('session_id', default='', type=int)
    no_session = request.args.get('no_session', default=0, type=bool)

    try:
        _user_ids = _user_ids.split(',') if _user_ids else []
        _user_ids = list(map(int, _user_ids))
    except ValueError:
        abort(404)
    selected_search_objects = db_sess.query(User).filter(User.id.in_(_user_ids))
    selected_search_objects = selected_search_objects.all()
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
            filter(User.id.notin_(_user_ids))
        selectable_search_objects = search_objects
        if group_id:
            members = db_sess.query(GroupMember.member_id).\
                filter(GroupMember.group_id == group_id)
            selectable_search_objects = selectable_search_objects.\
                filter(User.id.notin_(members))
        if session_id:
            members = db_sess.query(SessionMember.member_id).\
                filter(SessionMember.session_id == session_id)
            selectable_search_objects = selectable_search_objects.\
                filter(User.id.notin_(members))
        if no_session:
            members = db_sess.query(SessionMember.member_id)
            selectable_search_objects = selectable_search_objects. \
                filter(User.id.notin_(members))
        selectable_search_objects = selectable_search_objects.all()
        selectable_search_ids = [i.id for i in selectable_search_objects]

    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')
    return render_template('select_users.html', **locals())
