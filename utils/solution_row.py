from data.solution import Solution
from program_testing import prog_lang
from program_testing.message import get_message_solution
from utils.utils import date_format


def get_solution_row(solution):
    languages = prog_lang.get_languages()
    solution: Solution
    i = solution
    solution_row = []
    for x in [
        i.id, i.user.username,
        i.sent_date.strftime(date_format()),
        languages[i.lang_code_name].name,
        get_message_solution(i),
        f'{i.max_time:.3f}',
        f'{i.max_memory // 1024} Kb'
    ]:
        solution_row.append(x if type(
            x) == tuple else (x, ''))
    return solution_row
