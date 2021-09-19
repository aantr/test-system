from flask import url_for
from flask import render_template, redirect
from flask_login import current_user
from global_app import get_app

app = get_app()


@app.errorhandler(404)
def error404(error):
    if current_user.is_authenticated:
        return render_template('error_auth.html', code=404), 404
    return render_template('error.html', code=404), 404


@app.errorhandler(403)
def error401(error):
    if current_user.is_authenticated:
        return render_template('error_auth.html', code=403), 403
    return render_template('error.html', code=403), 403


@app.errorhandler(401)
def error401(error):
    if current_user.is_authenticated:
        return render_template('error.html', code=401), 401
    return redirect(url_for('login_'))
