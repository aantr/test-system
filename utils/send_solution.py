from data.user import User
from program_testing import test_program as tp

from data.solution import Solution
from data.source_code import SourceCode
from data.test_result import TestResult


def send_solution(problem_id, source, lang, session_id, user: User, db_sess):
    test_program = tp.get_test_program()

    source_code = SourceCode()
    db_sess.add(source_code)
    db_sess.flush()

    test_result = TestResult()
    db_sess.add(test_result)
    db_sess.flush()

    solution = Solution()
    solution.user_id = user.id
    solution.problem_id = problem_id
    solution.lang_code_name = lang
    solution.test_result = test_result
    solution.source_code = source_code
    solution.session_id = session_id

    db_sess.add(solution)
    db_sess.flush()

    test_program.add_solution(source, solution)
    test_program.add_to_queue(db_sess, solution)

    return solution
