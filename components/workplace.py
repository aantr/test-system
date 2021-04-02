from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from flask import url_for
from flask import render_template, redirect
from flask_login import login_required, current_user
from markupsafe import Markup
from components.session import check_session_timeout
from data import db_session
from data.session import Session, SessionMember
from data.solution import Solution
from data.user import User
from global_app import get_app
from utils.permissions_required import student_required
from utils.utils import get_session_joined, get_solution_row

current_user: User
app = get_app()

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
close_sessions_jobs = {}


@app.route('/workplace/status', methods=['GET'])
@student_required
def workplace_status():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    if not session:
        return redirect(url_for('action'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace_info'))

    solution = db_sess.query(Solution).filter(Solution.user_id == current_user.id). \
        filter(Solution.session_id == session.id).order_by(Solution.sent_date.desc()).all()
    solution_rows = [[Markup(render_template(
        'status_row.html',
        row=get_solution_row(i))), i.id] for i in solution]
    rows_to_update = [i.id for i in solution if not i.completed]
    update_timeout = current_app.config['UPDATE_STATUS_TIMEOUT']
    return render_template('workplace_status.html', **locals())


@app.route('/workplace/info', methods=['GET'])
@student_required
def workplace_info():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    if not session:
        return redirect(url_for('action'))
    check_session_timeout(db_sess, session)

    problem = session.problems

    return render_template('workplace_info.html', **locals())


@app.route('/workplace/problem', methods=['GET'])
@student_required
def workplace_problem():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    session: Session
    if not session:
        return redirect(url_for('action'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace_info'))

    problem = session.problems

    return render_template('workplace_problems.html', **locals())


@app.route('/workplace', methods=['GET'])
@student_required
def workplace():
    return redirect(url_for('workplace_problem'))


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


@app.route('/workplace/results', methods=['GET'])
@student_required
def workplace_results():
    db_sess = db_session.create_session()

    session = get_session_joined(db_sess)
    session: Session
    if not session:
        return redirect(url_for('action'))
    check_session_timeout(db_sess, session)
    if not session.started:
        return redirect(url_for('workplace_info'))

    problem_ids = [i.id for i in session.problems]
    problems_names = [i.name for i in session.problems]
    members = db_sess.query(SessionMember).filter(SessionMember.session_id == session.id).all()
    members = [i.member for i in members]
    result_rows = [render_template('result_row.html',
                                   row=get_result_row(db_sess, n, i, session, problem_ids))
                   for n, i in enumerate(members)]
    results = render_template('session_results.html', **locals())
    return render_template('workplace_results.html', **locals())


@app.route('/leave_session')
@student_required
def leave_session():
    db_sess = db_session.create_session()
    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id == current_user.id).delete()
    db_sess.commit()
    return redirect(url_for('action'))
