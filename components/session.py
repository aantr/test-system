from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, request, current_app
import datetime
from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from markupsafe import Markup

from components.action_link import add_action
from data import db_session
from data.group import Group, GroupMember
from data.invite import Invite
from data.problem import Problem
from data.session import Session, SessionMember
from data.solution import Solution
from data.user import User
from forms.submit_session import SubmitSessionForm
from global_app import get_app
from utils.permissions_required import student_required, teacher_required
from utils.utils import get_message_from_form, get_duration_from_time
from utils.solution_row import get_solution_row
from utils.result_row import get_result_row, render_result_rows

current_user: User
app = get_app()

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
close_sessions_jobs = {}


@app.route('/add_session', methods=['GET', 'POST'])
@teacher_required
def add_session():
    db_sess = db_session.create_session()
    form = SubmitSessionForm()

    problems = {str(i.id): i for i in db_sess.query(Problem).all()}
    form.problems.choices = [(str(k), v.name) for k, v in problems.items()]

    if form.validate_on_submit():

        session = Session()
        session.name = form.name.data
        session.description = form.description.data
        session.user_id = current_user.id
        session.duration = form.time.data

        db_sess.add(session)
        db_sess.flush()

        for i in form.problems.checked:
            session.problems.append(problems[i])

        flash(f'Successfully added session "{session.name}"', category='success')
        db_sess.commit()
        return redirect(url_for('add_session'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_session.html', form=form)


@app.route('/set_join_action_session/<int:session_id>')
@teacher_required
def set_join_action_session(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)

    session.join_action_str_id = add_action(
        db_sess, f'/invite_join_session/{session_id}',
        f'Send invite to join the session "{session.name}"',
        commit=False)
    db_sess.commit()
    return redirect(url_for('get_session', session_id=session_id))


@app.route('/start_session/<int:session_id>')
@teacher_required
def start_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if not session:
        abort(404)
    if session.user_id != current_user.id:
        abort(403)

    members = [i.member for i in db_sess.query(SessionMember).
        filter(SessionMember.session_id == session_id).all()]
    if not session.started:
        if not members:
            flash('In the session must be at least one member to start', category='danger')
        else:
            now = datetime.datetime.now()
            session.started = True
            session.start_date = now
            db_sess.commit()

            duration = get_duration_from_time(session.duration)
            job = scheduler.add_job(_stop_session, 'date', args=[session_id],
                                    run_date=now + duration)
            close_sessions_jobs[session_id] = job

    return redirect(url_for('get_session', session_id=session_id))


@app.route('/stop_session/<int:session_id>')
@teacher_required
def stop_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if not session:
        abort(404)
    if session.user_id != current_user.id:
        abort(403)

    if session.started:
        _stop_session(session.id, session=session, db_sess=db_sess)
        if session_id in close_sessions_jobs:
            close_sessions_jobs[session_id].remove()
            del close_sessions_jobs[session_id]

    return redirect(url_for('get_session', session_id=session_id))


def _stop_session(id, session=None, db_sess=None):
    if session is None:
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.id == id).first()
    if session.started:
        session.started = False
        session.start_date = None
        db_sess.commit()


def check_session_timeout(db_sess, session):
    if session.started:
        duration = get_duration_from_time(session.duration)
        if duration <= datetime.datetime.now() - session.start_date:
            _stop_session(session.id, session, db_sess)


@app.route('/my_sessions')
@teacher_required
def my_sessions():
    db_sess = db_session.create_session()
    time_left = {}
    sessions = db_sess.query(Session).filter(Session.user_id == current_user.id). \
        order_by(Session.created_date.desc()).all()
    for i in sessions:
        check_session_timeout(db_sess, i)
        if i.started:
            duration = datetime.datetime.combine(
                datetime.date.min, i.duration) - datetime.datetime.min
            delta = datetime.datetime.now() - i.start_date
            left = duration - delta
            time_left[i.id] = left.total_seconds()

    return render_template('my_sessions.html', **locals())


@app.route('/add_session_member', methods=['GET'])
@teacher_required
def add_session_member():
    db_sess = db_session.create_session()
    session_id = request.args.get('session_id', default='', type=int)
    user_ids = request.args.get('user_ids', default='', type=str)
    try:
        user_ids = list(map(int, user_ids.split(',')))
    except ValueError:
        abort(404)
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if session is None:
        abort(404)
    if session.user_id != current_user.id:
        abort(403)
    users = db_sess.query(User).filter(User.id.in_(user_ids)).all()
    if len(users) != len(user_ids):
        abort(404)

    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id.in_(user_ids)).first()

    if joined_session_member:
        flash(f'User "{joined_session_member.member.username}" already joined to any session',
              category='danger')
        return redirect(url_for('session_members', session_id=session_id))

    for i in user_ids:
        session: Session
        sm = SessionMember()
        sm.session_id = session_id
        sm.member_id = i
        db_sess.add(sm)
    db_sess.commit()
    flash(f'Successfully joined {len(user_ids)} user(s) to the session "{session.name}"', category='success')
    return redirect(url_for('session_members', session_id=session_id))


@app.route('/load_session_member_group', methods=['GET'])
@teacher_required
def load_session_member_group():
    db_sess = db_session.create_session()
    session_id = request.args.get('session_id', default='', type=int)
    group_id = request.args.get('group_id', default='', type=int)
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if session is None:
        abort(404)
    if session.user_id != current_user.id:
        abort(403)
    group: Group = db_sess.query(Group).filter(Group.id == group_id).first()
    if group is None:
        abort(404)
    if group.user_id != current_user.id:
        abort(403)
    db_sess.query(SessionMember).filter(SessionMember.session_id == session_id).delete()
    db_sess.flush()
    member_ids = db_sess.query(GroupMember.member_id).filter(GroupMember.group_id == group_id).all()
    for i in member_ids:
        member = SessionMember()
        member.member_id = i[0]
        member.session_id = session_id
        db_sess.add(member)
    db_sess.commit()
    flash(f'Successfully loaded session members from group "{group.name}"', category='success')
    return redirect(url_for('session_members', session_id=session_id))


@app.route('/invite_join_session/<int:session_id>', methods=['GET'])
@student_required
def invite_join_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if session is None:
        abort(404)
    session: Session
    url = 'action'

    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id == current_user.id). \
        filter(SessionMember.session_id == session_id).first()

    if joined_session_member:
        flash(f'Already joined to the session "{session.name}"', category='danger')
        return redirect(url_for(url))

    if db_sess.query(Invite).filter(Invite.user_from_id == current_user.id). \
            filter(Invite.user_to_id == session.user_id).first():
        flash(f'Already sent invite to the session "{session.name}"', category='danger')
        return redirect(url_for(url))

    invite = Invite()
    invite.user_from_id = current_user.id
    invite.user_to_id = session.user_id
    invite.action = f'/add_session_member?session_id={session_id}&user_ids={current_user.id}'
    invite.description = f'Join me to your session "{session.name}"'
    db_sess.add(invite)
    db_sess.commit()
    flash(f'Successfully sent invite to the session "{session.name}"', category='success')
    return redirect(url_for(url))


def get_session_by_id(db_sess, id):
    session = db_sess.query(Session).filter(Session.id == id).first()
    if not session:
        abort(404)
    check_session_timeout(db_sess, session)
    if session.user_id != current_user.id:
        abort(403)
    return session


@app.route('/session/results/<int:session_id>')
@teacher_required
def session_results(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)
    results = render_result_rows(db_sess, session)
    return render_template('session_results.html', **locals())


@app.route('/session/members/<int:session_id>')
@teacher_required
def session_members(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)
    members = [j.member for j in db_sess.query(SessionMember).
        filter(SessionMember.session_id == session_id).all()]
    session_id = str(session_id)
    return render_template('session_members.html', **locals())


@app.route('/session/problems/<int:session_id>')
@teacher_required
def session_problems(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)
    problems = session.problems
    return render_template('session_problems.html', **locals())


@app.route('/session/status/<int:session_id>')
@teacher_required
def session_status(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)

    solution = db_sess.query(Solution).filter(Solution.session_id == session.id). \
        order_by(Solution.sent_date.desc()).all()
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    update_timeout = current_app.config['UPDATE_STATUS_TIMEOUT']
    status_base = render_template('status_base.html', **locals())

    return render_template('session_status.html', **locals())


@app.route('/session/info/<int:session_id>')
@teacher_required
def session_info(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)
    time_left = session.get_time_left()
    return render_template('session_info.html', **locals())


@app.route('/session/<int:session_id>')
@teacher_required
def get_session(session_id):
    return redirect(url_for('session_info', session_id=session_id))


@app.route('/clear_members_session/<int:session_id>')
@teacher_required
def clear_members_session(session_id):
    db_sess = db_session.create_session()
    session = get_session_by_id(db_sess, session_id)
    if session.started:
        flash('Unable to remove member from a session during a started session',
              category='danger')
    else:
        db_sess.query(SessionMember). \
            filter(SessionMember.session_id == session_id).delete()
        db_sess.commit()
    flash('Successfully deleted all session members', category='success')
    return redirect(url_for('session_members', session_id=session_id))
