from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user

from components.action_link import add_action
from data.group import Group, GroupMember
from data.invite import Invite
from data.user import User
from forms.submit_group import SubmitGroupForm
from data import db_session
from global_app import get_app
from utils.utils import get_message_from_form

current_user: User
app = get_app()


@app.route('/groups', methods=['GET'])
@login_required
def groups():
    db_sess = db_session.create_session()
    groups = current_user.group

    return render_template('groups.html', **locals())


@app.route('/add_group', methods=['GET', 'POST'])
@login_required
def add_group():
    db_sess = db_session.create_session()
    form = SubmitGroupForm()

    if form.validate_on_submit():
        group = Group()
        group.user_id = current_user.id
        group.name = form.name.data
        db_sess.add(group)
        db_sess.commit()
        flash(f'Successfully added group "{group.name}"', category='success')
        return redirect(url_for('add_group'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_group.html', **locals())


@app.route('/groups/<int:group_id>', methods=['GET', 'POST'])
@login_required
def get_group(group_id):
    db_sess = db_session.create_session()

    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    if group.user_id != current_user.id:
        abort(401)

    members = [i.member for i in db_sess.query(GroupMember)
        .filter(GroupMember.group_id == group_id).all()]

    return render_template('group.html', **locals())


@app.route('/add_group_member/<int:group_id>/<int:user_id>', methods=['GET'])
@login_required
def add_group_member(group_id, user_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user is None:
        abort(404)
    if group.user_id != current_user.id:
        abort(401)

    joined_group_member = db_sess.query(GroupMember). \
        filter(GroupMember.member_id == user_id). \
        filter(GroupMember.group_id == group_id).first()

    if joined_group_member:
        flash(f'Already joined "{user.username}" to the group "{group.name}"', category='danger')
        return redirect(url_for('invites'))

    group: Group
    gm = GroupMember()
    gm.group_id = group_id
    gm.member_id = current_user.id
    db_sess.add(gm)
    db_sess.commit()
    flash(f'Successfully joined "{user.username}" to the group "{group.name}"', category='success')
    return redirect(url_for('invites'))


@app.route('/invite_join_group/<int:group_id>', methods=['GET'])
@login_required
def invite_join_group(group_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    group: Group
    url = 'action'

    joined_group_member = db_sess.query(GroupMember). \
        filter(GroupMember.member_id == current_user.id). \
        filter(GroupMember.group_id == group_id).first()

    if joined_group_member:
        flash(f'Already joined to the group "{group.name}"', category='danger')
        return redirect(url_for(url))

    if db_sess.query(Invite).filter(Invite.user_from_id == current_user.id). \
            filter(Invite.user_to_id == group.user_id).first():
        flash(f'Already sent invite to the group "{group.name}"', category='danger')
        return redirect(url_for(url))

    invite = Invite()
    invite.user_from_id = current_user.id
    invite.user_to_id = group.user_id
    invite.action = f'/add_group_member/{group_id}/{current_user.id}'
    invite.description = f'Join me to your group "{group.name}"'
    db_sess.add(invite)
    db_sess.commit()
    flash(f'Successfully sent invite to the group "{group.name}"', category='success')
    return redirect(url_for(url))


@app.route('/set_join_action_group/<int:group_id>')
@login_required
def set_join_action_group(group_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if not group:
        abort(404)
    if group.user_id != current_user.id:
        abort(401)
    group: Group
    group.join_action_str_id = add_action(
        db_sess, f'/invite_join_group/{group_id}',
        f'Send invite to join the group "{group.name}"',
        commit=False)
    db_sess.commit()
    print(group.join_action_str_id, group.join_action)
    return redirect(url_for('get_group', group_id=group_id))
