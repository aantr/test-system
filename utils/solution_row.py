from data.solution import Solution
from program_testing import prog_lang
from program_testing.message import get_message_solution
from utils.utils import datetime_format


def get_solution_row(solution):
    languages = prog_lang.get_languages()
    solution: Solution
    i = solution
    solution_row = {'row': [], 'problem_id': i.problem_id}
    for x in [
        i.id, i.user.username, i.problem.name,
        i.sent_date.strftime(datetime_format()),
        languages[i.lang_code_name].name,
        get_message_solution(i),
        i.get_max_time(),
        i.get_max_memory()
    ]:
        solution_row['row'].append(x if type(
            x) == tuple else (x, ''))
    return solution_row
