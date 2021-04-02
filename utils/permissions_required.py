from functools import wraps

from flask import current_app, abort
from flask_login import current_user, LoginManager, login_required

from data.user import User

current_user: User


def permissions_required(permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.type > permissions:
                abort(403)
                return
            return func(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(func):
    @wraps(func)
    @login_required
    @permissions_required(10)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated


def teacher_required(func):
    @wraps(func)
    @login_required
    @permissions_required(20)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated


def student_required(func):
    @wraps(func)
    @login_required
    @permissions_required(30)
    def decorated(*args, **kwargs):
        return func(*args, **kwargs)

    return decorated
