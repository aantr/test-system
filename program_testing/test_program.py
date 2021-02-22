import json
import os
import shutil
import time
from datetime import datetime
from subprocess import Popen, PIPE
import psutil

from program_testing.prog_lang import ProgLang, languages
from db_data import db_session
from db_data.problem import Problem
from db_data.solution import Solution

directory = os.path.dirname(__file__)
WRITE_SOLUTION_TIMEOUT = 0.3


class TestResult:
    def __init__(self):
        self.time = None
        self.memory = None
        self.stdout = None
        self.stderr = None


class TestProgram:
    def __init__(self):
        self.queue = []
        self.con = None

    def add_to_queue(self, session, solution):
        solution.state = 'In waiting queue'
        self.write_test_results(solution, [])
        self.write_solution(session, solution)
        self.queue.append(solution.id)

    def start(self):
        while True:
            time.sleep(0.1)
            if self.queue:
                solution_id = self.queue.pop(0)
                self.run_testing(solution_id)

    def run_testing(self, solution_id):
        db_sess = db_session.create_session()

        solution = self.read_solution(db_sess, solution_id)
        problem = self.read_problem(db_sess, solution.problem_id)

        solution.verdict = 'All correct'
        solution.success = 1
        solution.state = 'Compiling...'
        solution.max_time = 0
        solution.max_memory = 0
        solution.failed_test = 0
        solution.completed = 0

        self.write_solution(db_sess, solution)

        test_results = []
        lang: ProgLang = languages[solution.lang_code_name]
        name = 'solution.' + lang.extension
        source = os.path.join(directory, 'source_solution', name)
        path = os.path.join('solution', str(solution.id))
        shutil.copy(os.path.join(directory, path, 'solution.source'), source)

        compile_result = lang.compile(os.path.abspath(source))
        if not compile_result[0]:
            solution.success = 0
            solution.completed = 1
            solution.verdict = 'Compile error'
            solution.state = ''

            res = TestResult()
            res.stderr = compile_result[1].decode(lang.encoding)
            test_results.append(res)

            self.write_test_results(solution, test_results)
            self.write_solution(db_sess, solution)
            return

        check_proc_delay = 0.001
        write_solution_start = datetime.now()

        for i, (stdin, correct_answer) in enumerate(self.read_tests(problem)):
            new_test = True
            verdict = None
            success = 0
            current_memory, current_time = 0, 0
            stdout, stderr = None, None
            solution.state = f'Running on test {i + 1}...'

            proc = Popen(compile_result[1], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            proc.stdin.write(stdin.encode(lang.encoding))
            proc.stdin.close()
            start_time = datetime.now()
            run = True
            while run:
                try:
                    current_memory = self.get_memory(proc.pid)
                except psutil.NoSuchProcess:
                    # Из-за параллельного запуска процесс
                    # может отключиться и поднять исключение
                    ...
                if check_proc_delay:
                    time.sleep(check_proc_delay)

                delta = (datetime.now() - start_time).total_seconds()
                current_time = delta

                if current_time >= problem.time_limit:
                    verdict = 'Time limit error'
                    run = False
                if current_memory >= problem.memory_limit:
                    verdict = 'Memory limit error'
                    run = False

                delta = (datetime.now() - write_solution_start).total_seconds()
                if delta >= WRITE_SOLUTION_TIMEOUT and new_test:
                    new_test = False
                    write_solution_start = datetime.now()
                    self.write_solution(db_sess, solution, cols=('state',))

                if proc.poll() is not None:
                    code = proc.poll()
                    stdout = proc.stdout.read().strip().decode(lang.encoding)
                    stderr = proc.stderr.read().strip().decode(lang.encoding)
                    stdout, stderr = map(lambda x: x if x else None, [stdout, stderr])
                    if code:
                        verdict = 'Runtime error'
                    else:
                        if stdout == correct_answer:
                            success = True
                        else:
                            verdict = 'Wrong answer'
                    run = False
            proc.kill()

            res = TestResult()
            res.time = current_time
            res.memory = current_memory
            res.stdout = stdout
            res.stderr = stderr
            test_results.append(res)

            solution.max_time = max(solution.max_time, current_time)
            solution.max_memory = max(solution.max_memory, current_memory)
            if not success:
                solution.success = success
                solution.verdict = verdict
                solution.failed_test = i
                break
        solution.state = ''
        solution.completed = 1
        self.write_test_results(solution, test_results)
        self.write_solution(db_sess, solution)

    @staticmethod
    def add_solution(source, id):
        path = os.path.join(directory, 'solution', str(id))
        os.mkdir(path)
        with open(os.path.join(path, 'solution.source'), 'w') as f:
            f.write(source)

    @staticmethod
    def write_test_results(solution, test_results: list):
        path = os.path.join('solution', str(solution.id))
        with open(os.path.join(directory, path, 'test_results.json'), 'w') as f:
            json.dump([[x[1] for x in sorted(res.__dict__.items())] for res in test_results], f)

    @staticmethod
    def read_test_results(solution) -> list:
        path = os.path.join('solution', str(solution.id))
        res = []
        try:
            with open(os.path.join(directory, path, 'test_results.json'), 'r') as f:
                read = json.load(f)
        except FileNotFoundError:
            return res
        for i in read:
            t = TestResult()
            for n, j in enumerate(sorted(t.__dict__.keys())):
                setattr(t, j, i[n])
            res.append(t)
        return res

    @staticmethod
    def write_solution(session, solution, cols=None):
        if cols is None:
            cols = Solution.__table__.columns.keys()
        session.query(Solution).filter(Solution.id == solution.id).update(
            {column: getattr(Solution, column) for column in cols},
            synchronize_session=False
        )
        session.commit()

    @staticmethod
    def read_solution(session, id):
        return session.query(Solution).filter(Solution.id == id).first()

    @staticmethod
    def write_problem(session, problem):
        session.query(Problem).filter(Problem.id == problem.id).update(
            {column: getattr(Problem, column) for column in Problem.__table__.columns.keys()},
            synchronize_session=False
        )
        session.commit()

    @staticmethod
    def read_problem(session, id):
        return session.query(Problem).filter(Problem.id == id).first()

    @staticmethod
    def read_tests(problem, n=None):
        path = os.path.join('problem', str(problem.id))
        dir_path = os.path.join(directory, path, 'tests')
        res = []
        k = 0
        for root, dirs, files in os.walk(dir_path):
            for name in files:
                if os.path.splitext(name)[1] == '.in':
                    name_out = os.path.splitext(name)[0] + '.out'
                    with open(os.path.join(root, name)) as f_in:
                        with open(os.path.join(root, name_out)) as f_out:
                            res.append((f_in.read().strip(), f_out.read().strip()))
                            if k == n:
                                return [res[-1]]
                            k += 1
        if not res:
            raise FileNotFoundError(f'No tests on "{dir_path}"')
        return res

    @staticmethod
    def get_memory(pid):
        """Returns used memory in bytes"""
        process = psutil.Process(pid)
        return process.memory_info().rss
