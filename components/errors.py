from flask import url_for, flash, request
from flask import render_template, redirect, abort
from flask_login import login_required, current_user
from global_app import get_app

app = get_app()


@app.errorhandler(404)
def error404(error):
    return render_template('error.html', code=404), 404


@app.errorhandler(403)
def error401(error):
    return render_template('error.html', code=403), 403


@app.errorhandler(401)
def error401(error):
    if current_user.is_authenticated:
        return render_template('error.html', code=401), 401
    return redirect(url_for('login_'))
