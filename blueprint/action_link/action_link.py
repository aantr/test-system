from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, flash, url_for
import datetime
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from data import db_session
from data.action import Action
from data.user import User
from forms.action_link import ActionLinkForm
from utils.unique_code import get_code

current_user: User
action_bp = Blueprint('action_link', __name__,
                      template_folder='templates',
                      static_folder='static')

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()


def _stop_action(str_id):
    db_sess = db_session.create_session()
    action = db_sess.query(Action).filter(Action.str_id == str_id).first()
    if action is not None:
        db_sess.delete(action)
        db_sess.commit()


def clear_all_actions():
    db_sess = db_session.create_session()
    db_sess.query(Action).delete()
    db_sess.commit()


def add_action(db_sess, url, commit=True):
    action = Action()
    action.str_id = get_code().upper()
    action.url = url
    db_sess.add(action)
    if commit:
        db_sess.commit()
    else:
        db_sess.flush()

    duration = datetime.timedelta(seconds=60)
    job = scheduler.add_job(_stop_action, 'date', args=[action.str_id],
                            run_date=datetime.datetime.now() + duration)

    return action.str_id


@action_bp.route('/action_link/<str_id>', methods=['GET'])
@login_required
def action_link(str_id):
    db_sess = db_session.create_session()
    action = db_sess.query(Action).filter(Action.str_id == str_id).first()
    if action is None:
        abort(404)
    return redirect(action.url)


@action_bp.route('/action', methods=['GET', 'POST'])
@login_required
def action():
    db_sess = db_session.create_session()
    form = ActionLinkForm()

    if form.validate_on_submit():
        action = db_sess.query(Action).filter(
            Action.str_id == form.str_id.data.upper()).first()
        if action is None:
            flash('Incorrect action ID', category='danger')
        else:
            return redirect(url_for(f'action_link.action_link', str_id=action.str_id))
    return render_template('action_link.html', form=form)
