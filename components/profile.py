from flask import render_template, abort
from flask_login import current_user

from data.solution import Solution
from data.user import User
from global_app import get_app
from data import db_session
from utils.permissions_required import student_required

app = get_app()
current_user: User


@app.route('/profile/<int:id>', methods=['GET'])
@student_required
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        abort(404)
    if not current_user.has_rights_teacher() and current_user.id != id:
        abort(403)
    label = 'Profile statistic'
    colors = ['#f77', '#fa7', '#7af', '#77f']
    statistic = {
        'submits': 0,
        'success_solutions': 0,
        'submitted_problems': 0,
        'solved_problems': 0,
    }
    solutions = {}
    for i in user.solution:
        i: Solution
        statistic['submits'] += 1
        if i.success:
            statistic['success_solutions'] += 1
        if i.problem_id not in solutions:
            solutions[i.problem_id] = 0
            statistic['submitted_problems'] += 1
        if not solutions[i.problem_id]:
            if i.success:
                solutions[i.problem_id] = 1
                statistic['solved_problems'] += 1
    data = [(k.replace('_', ' ').capitalize(), v) for k, v in statistic.items()]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    if current_user.id == id:
        return render_template('myprofile.html', **locals())
    return render_template('profile.html', **locals())
