from datetime import timedelta

from flask import render_template, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from data import db_session
from data.user import User
from forms.login import LoginForm

from global_app import get_app
from utils.utils import get_message_from_form

app = get_app()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login_():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=False, duration=timedelta(minutes=1))
            return redirect('/')
        flash('Incorrect username or password', category='danger')
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('login.html', **locals())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
