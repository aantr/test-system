from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, current_app
from flask import url_for, flash
from flask import render_template, redirect, abort
from flask_login import login_required, current_user

from markupsafe import Markup

from blueprint.session.session import check_session_timeout
from data import db_session
from data.session import Session, SessionMember
from data.solution import Solution
from data.user import User
from utils import get_session_joined, get_solution_row

current_user: User
workplace_bp = Blueprint('workplace', __name__,
                         template_folder='templates',
                         static_folder='static')

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
close_sessions_jobs = {}


@workplace_bp.route('/workplace/status', methods=['GET'])
@login_required
def workplace_status():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    if not session:
        return redirect(url_for('workplace.join_session'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace.workplace_info'))

    # solution = sorted(filter(lambda x: x.session_id == session.id, current_user.solution),
    #                   key=lambda x: x.sent_date, reverse=True)
    solution = db_sess.query(Solution).filter(Solution.user_id == current_user.id). \
        filter(Solution.session_id == session.id).order_by(Solution.sent_date.desc()).all()
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    return render_template('workplace_status.html', **locals(),
                           update_timeout=current_app.config['UPDATE_STATUS_TIMEOUT'])


@workplace_bp.route('/workplace/info', methods=['GET'])
@login_required
def workplace_info():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    if not session:
        return redirect(url_for('workplace.join_session'))
    check_session_timeout(db_sess, session)

    problem = session.problems

    return render_template('workplace_info.html', **locals())


@workplace_bp.route('/workplace/problem', methods=['GET'])
@login_required
def workplace_problem():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    session: Session
    if not session:
        return redirect(url_for('workplace.join_session'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace.workplace_info'))

    problem = session.problems

    return render_template('workplace_problems.html', **locals())


@workplace_bp.route('/workplace', methods=['GET'])
@login_required
def workplace():
    return redirect(url_for('workplace.workplace_problem'))


@workplace_bp.route('/workplace/join_session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def join_session(session_id):
    db_sess = db_session.create_session()

    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id == current_user.id).first()

    if joined_session_member:
        return redirect(url_for('workplace.workplace'))

    session = db_sess.query(Session). \
        filter(Session.id == session_id).first()
    if not session:
        abort(404)
    else:
        joined_session_member = SessionMember()
        joined_session_member.member_id = current_user.id
        joined_session_member.session_id = session.id
        db_sess.add(joined_session_member)
        db_sess.commit()
    return redirect(url_for('workplace.workplace'))


def get_result_row(db_sess, n, user, session, problem_ids):
    send = {}
    for i in problem_ids:
        send[i] = [0, False]
    solutions = db_sess.query(Solution).filter(Solution.session_id == session.id). \
        filter(Solution.user_id == user.id).all()
    for i in solutions:
        send[i.problem_id][0] += 1
        if i.success:
            send[i.problem_id][1] = True
    row = [[0, n + 1], [0, user.username]]
    for i in problem_ids:
        row.append([1, *send[i]])
    return row


@workplace_bp.route('/workplace/results', methods=['GET'])
@login_required
def workplace_results():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    session: Session
    if not session:
        return redirect(url_for('workplace.join_session'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace.workplace_info'))

    problem_ids = [i.id for i in session.problems]
    problems_names = [i.name for i in session.problems]
    members = db_sess.query(SessionMember).filter(SessionMember.session_id == session.id).all()
    members = [i.member for i in members]
    result_rows = [render_template('result_row.html',
                                   row=get_result_row(db_sess, n, i, session, problem_ids))
                   for n, i in enumerate(members)]

    return render_template('session_results.html', **locals())


@workplace_bp.route('/leave_session')
@login_required
def leave_session():
    db_sess = db_session.create_session()
    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id == current_user.id).delete()
    db_sess.commit()
    return redirect(url_for('workplace.join_session'))
