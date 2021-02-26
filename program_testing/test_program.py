import json
import os
import shutil
import threading
import time
import zipfile
from datetime import datetime
from subprocess import Popen, PIPE
from zipfile import ZipFile
import psutil
from program_testing.prog_lang import ProgLang, languages
from data import db_session
from data.problem import Problem
from data.solution import Solution
from io import BytesIO

directory = os.path.dirname(__file__)
write_solution_timeout = 0.3
DEBUG = True


def set_write_solution_timeout(value):
    global write_solution_timeout
    write_solution_timeout = value


class TestResult:
    def __init__(self):
        self.time = None
        self.memory = None
        self.stdout = None
        self.stderr = None


class TestProgram:
    def __init__(self):
        self.queue = []

    def add_to_queue(self, session, solution):
        solution.state = 0
        solution.state_arg = len(self.queue)
        solution.max_time = 0
        solution.max_memory = 0
        solution.completed = 0
        self.queue.append(solution.id)
        self.write_test_results(solution, [])
        self.write_solution(session, solution)

    def start(self, threads=1):
        print('[Test system] Clear source folder')
        folder = os.path.join(directory, 'source_solution')
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('[Test system] Failed to delete %s. Reason: %s' % (file_path, e))

        for i in range(threads):
            thread_name = f'thread_{i + 1}'
            source_dir = os.path.join(folder, thread_name)
            os.mkdir(source_dir)
            t = threading.Thread(target=self._thread, args=(source_dir,))
            t.daemon = True
            t.start()

    def _get_from_queue(self, db_sess):
        solution_id = self.queue.pop(0)
        db_sess.query(Solution).filter(Solution.id.in_(self.queue[1:])). \
            update({Solution.state_arg: Solution.state_arg - 1},
                   synchronize_session=False)
        db_sess.commit()

        return solution_id

    def _thread(self, source_dir):
        db_sess = db_session.create_session()

        while True:
            time.sleep(0.05)
            if self.queue:
                try:
                    solution_id = self._get_from_queue(db_sess)
                except IndexError as e:
                    if DEBUG:
                        print('error', e)
                else:
                    self._run_testing(solution_id, db_sess, source_dir)

    def _run_testing(self, solution_id, db_sess, source_dir):

        solution = self.read_solution(db_sess, solution_id)
        problem = self.read_problem(db_sess, solution.problem_id)
        if solution is None:
            raise ValueError(f'[Test system] Impossible to get such solution id: {solution_id}')
        if problem is None:
            raise ValueError(f'[Test system] Impossible to get such problem id: {solution.problem_id}')
        tests = self.read_tests(problem)

        solution.success = 1
        solution.state = 1
        solution.state_arg = None

        self.write_solution(db_sess, solution)

        test_results = []
        lang: ProgLang = languages[solution.lang_code_name]
        name = 'solution.' + lang.extension
        source = os.path.join(source_dir, name)
        path = os.path.join('solution', str(solution.id))
        shutil.copy(os.path.join(directory, path, 'solution.source'), source)

        compile_result = lang.compile(os.path.abspath(source))
        if not compile_result[0]:
            solution.success = 0
            solution.completed = 1
            solution.state = 11

            res = TestResult()
            res.stderr = compile_result[1].decode(lang.encoding)
            test_results.append(res)

            self.write_test_results(solution, test_results)
            self.write_solution(db_sess, solution)
            return

        check_proc_delay = 0.001
        write_solution_start = datetime.now()
        verdict = 10
        max_time = 0
        max_memory = 0

        for i, (stdin, correct_answer) in enumerate(tests):
            new_test = True

            success = 0
            current_memory, current_time = 0, 0
            stdout, stderr = None, None
            solution.state = 2
            solution.state_arg = i

            proc = Popen(compile_result[1], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            proc.stdin.write(stdin.encode(lang.encoding))
            proc.stdin.close()
            start_time = datetime.now()
            run = True
            if DEBUG:
                prev_time = datetime.now()
                count = 0
                summary = 0
            while run:
                if DEBUG:
                    count += 1
                    summary += (datetime.now() - prev_time).total_seconds()
                    prev_time = datetime.now()
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
                    verdict = 13
                    run = False
                if current_memory >= problem.memory_limit:
                    verdict = 14
                    run = False

                delta = (datetime.now() - write_solution_start).total_seconds()
                if delta >= write_solution_timeout and new_test:
                    new_test = False
                    write_solution_start = datetime.now()
                    self.write_solution(db_sess, solution, cols=('state', 'state_arg'))

                if proc.poll() is not None:
                    code = proc.poll()
                    stdout = proc.stdout.read().strip().decode(lang.encoding)
                    stderr = proc.stderr.read().strip().decode(lang.encoding)
                    stdout, stderr = map(lambda x: x if x else None, [stdout, stderr])
                    if code:
                        verdict = 12
                    else:
                        if stdout == correct_answer:
                            success = True
                        else:
                            verdict = 15
                    run = False

            if DEBUG:
                print(f'[Test system DEBUG] Delta time of proc: {summary / count:.7f}')

            proc.kill()

            res = TestResult()
            res.time = current_time
            res.memory = current_memory
            res.stdout = stdout
            res.stderr = stderr
            test_results.append(res)

            max_time = max(max_time, current_time)
            max_memory = max(max_memory, current_memory)
            if not success:
                solution.success = success
                solution.failed_test = i
                break
        solution.completed = 1
        solution.state = verdict
        solution.state_arg = None
        solution.max_time = max_time
        solution.max_memory = max_memory
        self.write_test_results(solution, test_results)
        self.write_solution(db_sess, solution)

    @staticmethod
    def add_solution(source, id):
        path = os.path.join(directory, 'solution', str(id))
        try:
            os.mkdir(path)
        except FileExistsError:
            raise FileExistsError(f'[Test system] Such solution already created: {id}')
        finally:
            with open(os.path.join(path, 'solution.source'), 'wb') as f:
                f.write(source)

    @staticmethod
    def add_problem(id, bytes_zip_tests, task):
        path = os.path.join(directory, 'problem', str(id))
        try:
            os.mkdir(path)
        except FileExistsError:
            raise FileExistsError(f'[Test system] Such solution already created: {id}')
        finally:
            with open(os.path.join(path, 'task.txt'), 'w') as f:
                f.write(task)
            try:
                os.mkdir(os.path.join(path, 'tests'))
            except FileExistsError:
                ...
            temp_filename = os.path.join(path, 'arch.zip')
            with open(temp_filename, 'wb') as f:
                f.write(bytes_zip_tests)
            shutil.unpack_archive(temp_filename, os.path.join(path, 'tests'))
            os.remove(temp_filename)

    @staticmethod
    def remove_solution(id):
        path = os.path.join(directory, 'solution', str(id))
        try:
            os.remove(path)
        except FileNotFoundError:
            raise ValueError(f'[Test system] Such solution not found: {id}')

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
    def write_solution(session, solution, cols=None, commit=True):
        if DEBUG:
            start = datetime.now()
        if cols is None:
            cols = Solution.__table__.columns.keys()
        session.query(Solution).filter(Solution.id == solution.id).update(
            {column: getattr(Solution, column) for column in cols},
            synchronize_session=False
        )
        if commit:
            session.commit()
        if DEBUG:
            print(f'[Test system DEBUG] --- Time of writing solution ---: '
                  f'{(datetime.now() - start).total_seconds():.7f}')

    @staticmethod
    def read_solution(session, id):
        return session.query(Solution).filter(Solution.id == id).first()

    @staticmethod
    def write_problem(session, problem, cols=None, commit=True):
        if cols is None:
            cols = Problem.__table__.columns.keys()
        session.query(Problem).filter(Problem.id == problem.id).update(
            {column: getattr(Problem, column) for column in cols},
            synchronize_session=False
        )
        if commit:
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
            raise FileNotFoundError(f'[Test system] No tests on "{dir_path}"')
        return res

    @staticmethod
    def check_tests_zip(bytes):
        s1 = set()
        try:
            with ZipFile(BytesIO(bytes)) as z:
                files = z.namelist()
                for name in files:
                    filename = os.path.split(name)[1]
                    path_w = os.path.join(os.path.split(name)[0],
                                          os.path.splitext(filename)[0])
                    if os.path.splitext(filename)[1] == '.in':
                        s1.add(path_w)
                    elif os.path.splitext(filename)[1] == '.out':
                        if path_w in s1:
                            s1.remove(path_w)
                        else:
                            return False
        except zipfile.error as e:
            if DEBUG:
                print(e)
            return False
        if s1:
            return False
        return True

    @staticmethod
    def get_memory(pid):
        """Returns used memory in bytes"""
        process = psutil.Process(pid)
        return process.memory_info().rss
