import os
import threading
import time

from data.problem import Problem
from data.solution import Solution
from program_testing import test_program as tp

import global_app
from data import db_session
from data.user import User
from program_testing.message import get_message_solution
from program_testing.test_program import TestProgram
from utils.send_solution import send_solution


def test_checker(app):
    test_program: TestProgram = tp.get_test_program()
    thread = threading.Thread(target=test_program.start, args=(), daemon=True,
                              kwargs={'threads': app.config['TEST_THREADS']})
    thread.start()
    time.sleep(0.5)

    db_sess = db_session.create_session()

    source = b'''
    a,b=map(int, input().split())
    print(a+b)
    '''

    sol = send_solution(
        db_sess.query(Problem).first().id,
        source, 'python', None, db_sess.query(User).first(), db_sess)
    sol_id = sol.id

    while 1:
        time.sleep(0.5)
        sol: Solution = db_sess.query(Solution).filter(Solution.id == sol_id).first()
        print(f'status ({sol.id}):', get_message_solution(sol))
        if sol.completed:
            break
