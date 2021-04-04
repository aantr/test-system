from data import db_session
from data.action import Action
from data.solution import Solution
from program_testing.test_program import TestProgram
from program_testing import test_program


def init_db():
    db_sess = db_session.create_session()
    clear_actions(db_sess)
    abort_solutions(db_sess)


def clear_actions(db_sess):
    db_sess.query(Action).delete()
    db_sess.commit()


def abort_solutions(db_sess):
    solutions = db_sess.query(Solution).filter(Solution.completed == 0).all()
    error = '[Test system] Abort testing solution (id={}), ' \
            'server just started and there is still not completed solution'
    for i in solutions:
        if test_program.DEBUG:
            print(error.format(i.id))
        TestProgram.abort_testing(db_sess, i, error.format(i.id), [], commit=False)
    db_sess.commit()
