from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user

from blueprint.action_link.action_link import add_action
from data.group import Group, GroupMember
from data.invite import Invite
from data.user import User
from forms.submit_group import SubmitGroupForm

from data import db_session

from flask import Blueprint

from utils.utils import get_message_from_form

current_user: User
invite_bp = Blueprint('invite', __name__,
                      template_folder='templates',
                      static_folder='static')


@invite_bp.route('/invites', methods=['GET'])
@login_required
def invites():
    db_sess = db_session.create_session()

    invites = db_sess.query(Invite).filter(
        Invite.user_to_id == current_user.id).all()

    return render_template('invites.html', **locals())


@invite_bp.route('/accept_invite/<int:invite_id>', methods=['GET'])
@login_required
def accept_invite(invite_id):
    db_sess = db_session.create_session()
    invite = db_sess.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        abort(404)
    if invite.user_to_id != current_user.id:
        abort(401)
    url = invite.action
    db_sess.query(Invite).filter(Invite.id == invite_id).delete()
    db_sess.commit()
    return redirect(url)
