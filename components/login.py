from flask import render_template, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from data import db_session
from data.user import User
from forms.login import LoginForm

from global_app import get_app

app = get_app()


@app.route('/login', methods=['GET', 'POST'])
def login_():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect('/')
        flash('Incorrect username or password', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
