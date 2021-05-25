from functools import wraps
from flask import abort
from flask_login import current_user, login_required
from data.user import User

current_user: User


def permissions_required(permissions: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            d = {'student': current_user.has_rights_student,
                 'teacher': current_user.has_rights_teacher,
                 'admin': current_user.has_rights_admin}
            if not d.get(permissions)():
                abort(403)
                return
            return func(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(func):
    @wraps(func)
    @login_required
    @permissions_required('admin')
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated


def teacher_required(func):
    @wraps(func)
    @login_required
    @permissions_required('teacher')
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated


def student_required(func):
    @wraps(func)
    @login_required
    @permissions_required('student')
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated
