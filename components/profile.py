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
    statistic = get_statistic(user)
    if not user:
        abort(404)
    if not current_user.has_rights_teacher() and current_user.id != id:
        abort(403)
    if current_user.id == id:
        return render_template('myprofile.html', **locals())
    return render_template('profile.html', **locals())


def get_statistic(user):
    statistic = {
        'solutions': len(user.solution),
        'success_solutions': 0
    }
    for i in user.solution:
        i: Solution
        if i.success:
            statistic['success_solutions'] += 1
    return statistic
