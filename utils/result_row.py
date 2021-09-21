import datetime

from flask import render_template

from data.session import SessionMember, Session
from data.solution import Solution
from utils.utils import datetime_format


def get_result_row(db_sess, user, session: Session, problem_ids):
    send = {}
    for i in problem_ids:
        send[i] = [0, False, None]
    solutions = db_sess.query(Solution).filter(Solution.session_id == session.id). \
        filter(Solution.completed == 1). \
        filter(Solution.user_id == user.id).order_by(Solution.sent_date).all()
    total_success_attempts = 0
    ignore_states = [11, 19]
    for i in solutions:
        i: Solution
        if not send[i.problem_id][1] and i.state not in ignore_states:
            send[i.problem_id][0] += 1
        if i.success and not send[i.problem_id][1]:
            send[i.problem_id][1] = True
            send[i.problem_id][2] = i.sent_date
            total_success_attempts += send[i.problem_id][0]
    row = [[0, 0], [0, user.username]]
    for i in problem_ids:
        row.append([1, *send[i]])
    total = 0
    penalty = 0
    last_correct_send = None
    for i in problem_ids:
        if send[i][1]:
            penalty += 10 * (send[i][0] - 1)
            total += 1
            if last_correct_send is None or send[i][2] > last_correct_send:
                last_correct_send = send[i][2]
    if last_correct_send and session.start_date:
        penalty += (last_correct_send - session.start_date).total_seconds() // 60
    if last_correct_send:
        row.append([0, last_correct_send.strftime(datetime_format())])
    else:
        row.append([1, 0])
    row.append([0, int(penalty)])
    row.append([0, total])
    return row, last_correct_send, total_success_attempts


def render_result_rows(db_sess, session):
    problem_ids = [i.id for i in session.problems]
    problems_names = [i.name for i in session.problems]
    members = [j.member for j in db_sess.query(SessionMember).
        filter(SessionMember.session_id == session.id).all()]
    rows = [get_result_row(db_sess, i, session, problem_ids) for n, i in enumerate(members)]
    rows = sorted(rows, key=lambda x: (-x[0][-1][1], x[0][-2][1], x[2], x[1]))
    for n, i in enumerate(rows):
        i[0][0][1] = n + 1
    result_rows = [render_template('result_row.html',
                                   row=rows[n][0]) for n, i in enumerate(members)]
    results = render_template('results_base.html', **locals())
    return results
