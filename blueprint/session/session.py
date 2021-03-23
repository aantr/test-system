from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, current_app
import datetime
from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
import uuid

from markupsafe import Markup

from blueprint.action_link.action_link import add_action
from data import db_session
from data.problem import Problem
from data.session import Session, SessionMember
from data.solution import Solution
from data.user import User
from forms.action_link import ActionLinkForm
from forms.submit_session import SubmitSessionForm
from utils import get_message_from_form, get_session_joined, get_solution_row, get_duration_from_time

current_user: User
session_bp = Blueprint('session', __name__,
                       template_folder='templates',
                       static_folder='static')

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
close_sessions_jobs = {}


@session_bp.route('/add_session', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('session.add_session'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')

    return render_template('add_session.html', form=form)


@session_bp.route('/set_join_action_session/<int:session_id>')
@login_required
def set_join_action_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if not session:
        abort(404)

    session.join_action_str_id = add_action(
        db_sess, f'/workplace/join_session/{session_id}', commit=False)
    db_sess.commit()
    return redirect(url_for('session.get_session', session_id=session_id))


@session_bp.route('/start_session/<int:session_id>')
@login_required
def start_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if not session:
        abort(404)

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

    return redirect(url_for('session.get_session', session_id=session_id))


@session_bp.route('/stop_session/<int:session_id>')
@login_required
def stop_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id).first()
    if not session:
        abort(404)

    if session.started:
        _stop_session(session.id, session=session, db_sess=db_sess)
        if session_id in close_sessions_jobs:
            close_sessions_jobs[session_id].remove()
            del close_sessions_jobs[session_id]

    return redirect(url_for('session.get_session', session_id=session_id))


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


@session_bp.route('/my_sessions')
@login_required
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


@session_bp.route('/session/<int:session_id>')
@login_required
def get_session(session_id):
    db_sess = db_session.create_session()
    session = db_sess.query(Session).filter(Session.id == session_id). \
        filter(Session.user_id == current_user.id).first()
    if not session:
        abort(404)
    check_session_timeout(db_sess, session)

    time_left = None
    members = None
    if session.started:
        duration = datetime.datetime.combine(
            datetime.date.min, session.duration) - datetime.datetime.min
        delta = datetime.datetime.now() - session.start_date
        left = duration - delta
        time_left = left.total_seconds()

    members = [j.member for j in db_sess.query(SessionMember).
        filter(SessionMember.session_id == session.id).all()]

    return render_template('session.html', **locals())
