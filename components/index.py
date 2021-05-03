from flask import render_template
from flask_login import login_required
from global_app import get_app
from utils.permissions_required import student_required

app = get_app()


@app.route('/')
@app.route('/index')
@student_required
def index():
    return render_template('index.html')


@app.route('/are_u_ok')
def are_u_ok():
    return 'ok'
