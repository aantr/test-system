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
current_user: User


@app.route('/select_group', methods=['GET', 'POST'])
@student_required
def select_group():
    db_sess = db_session.create_session()
    _return = request.args.get('return', default='', type=str)
    groups = current_user.group
    return render_template('select_group.html', **locals())
