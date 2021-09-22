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
from data.verification_code import VerificationCode
from forms.confirm_email import ConfirmEmailForm
from forms.register import RegisterForm

from global_app import get_app, get_dir
from utils.unique_code import get_code6
from utils.utils import get_message_from_form
from utils.send_mail import send_mail

app = get_app()
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])


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

        token = ts.dumps(form.email.data, salt=app.config['MAIL_CONFIRM_SECRET_KEY'])
        db_sess.query(User).filter(User.email == form.email.data).delete()
        db_sess.flush()
        user = User()
        user.confirmed_email = 0
        user.username = form.username.data
        user.set_password(form.password.data)
        user.email = form.email.data
        db_sess.add(user)
        vcode = VerificationCode(str_id=get_code6(), token=token)
        db_sess.add(vcode)
        db_sess.commit()

        html = render_template(
            'confirm_email.html',
            name=user.username,
            code=vcode.str_id
        )
        print(html)
        try:
            send_mail(app.config['MAIL_LOGIN'], form.email.data, 'Confirm email', '', html)
        except Exception as e:
            flash('Oops... Error with sending email. Please try again', category='danger')
            return render_template('register.html', **locals())

        flash('Successfully signed up, please confirm your email', category='info')
        return redirect(url_for('confirm_email', username=user.username))
    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')
    return render_template('register.html', **locals())


@app.route('/confirm/<username>', methods=['GET', 'POST'])
def confirm_email(username):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    if not user:
        flash('No such username', category='danger')
        return redirect(url_for('login_'))
    if user.confirmed_email:
        flash('Already confirmed email', category='info')
        return redirect(url_for('login_'))

    form = ConfirmEmailForm()
    if form.validate_on_submit():
        vcode = db_sess.query(VerificationCode).filter(VerificationCode.str_id == form.code.data.strip()).first()
        msg_incorrect = 'Incorrect verification code, please try again'
        if not vcode:
            flash(msg_incorrect, category='danger')
            return render_template('confirm.html', **locals())
        try:
            email = ts.loads(vcode.token, salt=app.config['MAIL_CONFIRM_SECRET_KEY'], max_age=86400)
        except Exception as e:
            flash(msg_incorrect, category='danger')
            return render_template('confirm.html', **locals())
        if user.email != email:
            flash(msg_incorrect, category='danger')
            return render_template('confirm.html', **locals())
        db_sess.delete(vcode)
        user.confirmed_email = True
        db_sess.commit()
        flash('Successfully confirmed email, please login', category='success')
        return redirect(url_for('login_', username=user.username))
    else:
        for i in get_message_from_form(form):
            flash(i, category='danger')

    return render_template('confirm.html', **locals())
