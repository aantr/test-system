import datetime

from flask_login import current_user

from data.session import SessionMember


def get_message_from_form(form):
    for i in form.__dict__.values():
        if hasattr(i, 'errors'):
            if i.errors:
                msg = f'{i.label.text}: {i.errors[0]}'
                return msg
    return ''


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


def date_format():
    return '%d %B %Y, %H:%M'
