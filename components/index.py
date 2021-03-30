from flask import render_template
from flask_login import login_required
from global_app import get_app

app = get_app()


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')
