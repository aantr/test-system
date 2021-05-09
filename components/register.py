import os
from datetime import timedelta

from flask import render_template, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from sqlalchemy import or_, and_
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.orm import Query
from werkzeug.exceptions import abort

from data import db_session
from data.user import User
from forms.register import RegisterForm

from global_app import get_app, get_dir
from utils.utils import get_message_from_form
from utils.send_mail import send_mail

app = get_app()
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
from_ = 'a@a.com'
subject = 'Confirm email'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(and_(or_(User.username == form.username.data,
                                                   User.email == form.email.data),
                                               User.confirmed_email == 1)).first()
        if user:
            flash('User with such username or email already exists', category='danger')
            return render_template('register.html', **locals())
        if form.password.data != form.repeat_password.data:
            flash('Passwords don\'t match', category='danger')
            return render_template('register.html', **locals())
        if len(form.password.data) < 6:
            flash('Password length must be at least 6', category='danger')
            return render_template('register.html', **locals())
        db_sess.query(User).filter(User.email == form.email.data).delete()
        db_sess.flush()
        user = User()
        user.confirmed_email = 0
        user.username = form.username.data
        user.set_password(form.password.data)
        user.email = form.email.data
        db_sess.add(user)
        db_sess.commit()
        token = ts.dumps(form.email.data, salt=app.config['MAIL_CONFIRM_SECRET_KEY'])
        confirm_url = url_for(
            'confirm_email',
            token=token,
            _external=True)
        text = ''
        html = render_template(
            'confirm_email.html',
            name=user.username,
            confirm_url=confirm_url
        )
        send_mail(from_, form.email.data, subject, text, html)

        flash('Successfully signed up, please confirm your email', category='success')
        return redirect(url_for('login_'))
    else:
        msg = get_message_from_form(form)
        if msg:
            flash(msg, category='danger')
    return render_template('register.html', **locals())


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt=app.config['MAIL_CONFIRM_SECRET_KEY'], max_age=86400)
    except Exception:
        abort(404)
        return
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if not user:
        abort(404)
    user.confirmed_email = True
    db_sess.commit()
    flash('Successfully confirmed email, please login', category='success')
    return redirect(url_for('login_'))
