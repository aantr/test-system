from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user

from blueprint.action_link.action_link import add_action
from data.group import Group, GroupMember
from data.user import User
from forms.submit_group import SubmitGroupForm

from data import db_session

from flask import Blueprint

from utils.utils import get_message_from_form

current_user: User
groups_bp = Blueprint('groups', __name__,
                      template_folder='templates',
                      static_folder='static')


@groups_bp.route('/groups', methods=['GET'])
@login_required
def groups():
    db_sess = db_session.create_session()
    groups = current_user.group

    return render_template('groups.html', **locals())


@groups_bp.route('/add_group', methods=['GET', 'POST'])
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
        return redirect(url_for('groups.add_group'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_group.html', **locals())


@groups_bp.route('/groups/<int:group_id>', methods=['GET', 'POST'])
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


@groups_bp.route('/join_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def join_group(group_id):
    db_sess = db_session.create_session()

    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)

    joined_group_member = db_sess.query(GroupMember). \
        filter(GroupMember.member_id == current_user.id). \
        filter(GroupMember.group_id == group_id).first()

    if joined_group_member:
        flash(f'Already joined to the group "{group.name}"', category='danger')
        return redirect(url_for('action_link.action'))

    group: Group
    gm = GroupMember()
    gm.group_id = group_id
    gm.member_id = current_user.id
    db_sess.add(gm)
    db_sess.commit()
    flash(f'Successfully joined to the group "{group.name}"', category='success')
    return redirect(url_for('action_link.action'))


@groups_bp.route('/set_join_action_group/<int:group_id>')
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
        db_sess, f'/join_group/{group_id}', commit=False)
    db_sess.commit()
    print(group.join_action_str_id, group.join_action)
    return redirect(url_for('groups.get_group', group_id=group_id))
