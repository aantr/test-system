from flask import render_template
from flask_login import login_required
from global_app import get_app
from program_testing import test_program as tp

app = get_app()


@app.route('/server_state')
@login_required
def server_state():
    test_program = tp.get_test_program()
    queue = test_program.get_queue_length()
    threads = app.config['TEST_THREADS']
    return render_template('server_state.html',
                           queue=queue, threads=threads)
