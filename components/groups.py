from flask import url_for, flash, request
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from components.action_link import add_action
from data.group import Group, GroupMember
from data.invite import Invite
from data.user import User
from forms.egit_group import EditGroupForm
from forms.submit_group import SubmitGroupForm
from data import db_session
from global_app import get_app
from utils.permissions_required import teacher_required, student_required
from utils.utils import get_message_from_form

current_user: User
app = get_app()


@app.route('/groups', methods=['GET'])
@teacher_required
def groups():
    db_sess = db_session.create_session()
    groups = current_user.group

    return render_template('groups.html', **locals())


@app.route('/add_group', methods=['GET', 'POST'])
@teacher_required
def add_group():
    db_sess = db_session.create_session()
    form = SubmitGroupForm()
    if form.validate_on_submit():
        if db_sess.query(Group).filter(
                func.lower(Group.name) == func.lower(form.name.data)).first():
            flash('Group with such name already exists', category='danger')
            return render_template('add_group.html', **locals())
        group = Group()
        group.user_id = current_user.id
        group.name = form.name.data
        db_sess.add(group)
        db_sess.commit()
        flash(f'Successfully added group "{group.name}"', category='success')
        return redirect(url_for('groups'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_group.html', **locals())


@app.route('/groups/<int:group_id>', methods=['GET', 'POST'])
@teacher_required
def get_group(group_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    if group.user_id != current_user.id:
        abort(403)
    members = [i.member for i in db_sess.query(GroupMember)
        .filter(GroupMember.group_id == group_id).all()]
    group_id = str(group_id)
    form = EditGroupForm(
        name=group.name
    )
    if form.validate_on_submit():
        if db_sess.query(Group).filter(
                func.lower(Group.name) == func.lower(form.name.data)). \
                filter(Group.id != group.id).first():
            flash('Group with such name already exists', category='danger')
            return render_template('edit_group.html', **locals())
        group.name = form.name.data
        db_sess.commit()
        flash(f'Successfully edited group "{group.name}"', category='success')
        return redirect(url_for('groups'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('edit_group.html', **locals())


@app.route('/add_group_member', methods=['GET'])
@teacher_required
def add_group_member():
    db_sess = db_session.create_session()
    group_id = request.args.get('group_id', default='', type=str)
    user_ids = request.args.get('user_ids', default='', type=str)
    try:
        user_ids = list(map(int, user_ids.split(',')))
    except ValueError:
        abort(404)
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    if group.user_id != current_user.id:
        abort(403)
    users = db_sess.query(User).filter(User.id.in_(user_ids)).all()
    if len(users) != len(user_ids):
        abort(404)

    joined_group_member = db_sess.query(GroupMember). \
        filter(GroupMember.member_id.in_(user_ids)). \
        filter(GroupMember.group_id == group_id).first()
    joined_group_member: GroupMember

    if joined_group_member:
        flash(f'User "{joined_group_member.member.username}" already joined to the group "{group.name}"',
              category='danger')
        return redirect(url_for('get_group', group_id=group_id))

    for i in user_ids:
        group: Group
        gm = GroupMember()
        gm.group_id = group_id
        gm.member_id = i
        db_sess.add(gm)
    db_sess.commit()
    flash(f'Successfully joined {len(user_ids)} user(s) to the group "{group.name}"', category='success')
    return redirect(url_for('get_group', group_id=group_id))


@app.route('/invite_join_group/<int:group_id>', methods=['GET'])
@student_required
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
    invite.action = f'/add_group_member?group_id={group_id}&user_ids={current_user.id}'
    invite.description = f'Join me to your group "{group.name}"'
    db_sess.add(invite)
    db_sess.commit()
    flash(f'Successfully sent invite to the group "{group.name}"', category='success')
    return redirect(url_for(url))


@app.route('/set_join_action_group/<int:group_id>')
@teacher_required
def set_join_action_group(group_id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if not group:
        abort(404)
    if group.user_id != current_user.id:
        abort(403)
    group: Group
    group.join_action_str_id = add_action(
        db_sess, f'/invite_join_group/{group_id}',
        f'Send invite to join the group "{group.name}"',
        commit=False)
    db_sess.commit()
    return redirect(url_for('get_group', group_id=group_id))


@app.route('/delete_group/<int:id>', methods=['GET'])
@teacher_required
def delete_group(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    if not group:
        abort(404)
    db_sess.delete(group)
    db_sess.commit()
    flash(f'Successfully deleted group "{group.name}"', category='success')
    return redirect(url_for('groups'))
