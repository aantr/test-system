from datetime import timedelta

from flask import render_template, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import abort

from data import db_session
from data.user import User
from forms.register import RegisterForm

from global_app import get_app
from utils.utils import get_message_from_form

app = get_app()
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
salt = 'email-confirm-key'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(or_(User.username == form.username.data,
                                              User.email == form.email.data)).first()
        if user:
            flash('User with such username or email already exists', category='danger')
            return render_template('register.html', **locals())
        if form.password.data != form.repeat_password.data:
            flash('Passwords don\'t match', category='danger')
            return render_template('register.html', **locals())
        if len(form.password.data) < 6:
            flash('Password length must be at least 6', category='danger')
            return render_template('register.html', **locals())
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        db_sess.add(user)
        db_sess.commit()
        subject = 'Confirm your email'
        print('ok')

        token = ts.dumps(form.email.data, salt=salt)

        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)

        html = render_template(
            'confirm_email.html',
            confirm_url=confirm_url)
        # send_email(user.email, subject, html)
        return render_template(url_for())
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('register.html', **locals())


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt=salt, max_age=86400)
    except Exception:
        abort(404)
        return
    db_sess = db_session.create_session()
    user = User.query.filter(User.email == email).first_or_404()
    user.confirmed_email = True
    db_sess.commit()

    return redirect(url_for('login_'))
