from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from data.invite import Invite
from data.user import User
from data import db_session
from global_app import get_app

current_user: User
app = get_app()


@app.route('/invites', methods=['GET'])
@login_required
def invites():
    db_sess = db_session.create_session()

    invites = db_sess.query(Invite).filter(
        Invite.user_to_id == current_user.id).all()

    return render_template('invites.html', **locals())


@app.route('/accept_invite/<int:invite_id>', methods=['GET'])
@login_required
def accept_invite(invite_id):
    db_sess = db_session.create_session()
    invite = db_sess.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        abort(404)
    if invite.user_to_id != current_user.id:
        abort(403)
    url = invite.action
    db_sess.query(Invite).filter(Invite.id == invite_id).delete()
    db_sess.commit()
    return redirect(url)
