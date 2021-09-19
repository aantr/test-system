import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import Field

from data.session import SessionMember


def get_message_from_form(form: FlaskForm):
    res = []
    for i in form.__dict__.values():
        i: Field
        if hasattr(i, 'errors'):
            if i.errors:
                res.append(f'{i.label.text}: {i.errors[0]}')
    return res[:1]


def get_session_joined(db_sess):
    joined_session_member = db_sess.query(SessionMember). \
        filter(SessionMember.member_id == current_user.id).first()
    if not joined_session_member:
        return
    return joined_session_member.session


def get_duration_from_time(time):
    duration = datetime.datetime.combine(
        datetime.date.min, time) - datetime.datetime.min
    return duration


def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def datetime_format():
    return '%d %B %Y, %H:%M'
