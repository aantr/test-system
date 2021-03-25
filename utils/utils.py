import datetime

from flask_login import current_user

from data.session import SessionMember
from program_testing import prog_lang
from program_testing.message import get_message_solution


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
    joined_session_member
    return joined_session_member.session


def get_solution_row(solution):
    languages = prog_lang.get_languages()
    i = solution
    solution_row = [x if type(
        x) == tuple else (x, '') for x in [
                        i.id, i.sent_date.strftime("%d %B %Y, %I:%M%p"),
                        languages[i.lang_code_name].name,
                        get_message_solution(i),
                        f'{i.max_time:.3f}',
                        f'{i.max_memory // 1024} Kb'
                    ]]
    return solution_row


def get_duration_from_time(time):
    duration = datetime.datetime.combine(
        datetime.date.min, time) - datetime.datetime.min
    return duration


