import json
import os
import shutil
import threading
import time
import zipfile
from zipfile import ZipFile
import psutil

from global_app import get_dir
from program_testing import prog_lang
from program_testing.create_process import create_process, get_source_solution
from program_testing.prog_lang import ProgLang
from data import db_session
from data.problem import Problem
from data.solution import Solution
from io import BytesIO

directory = os.path.dirname(__file__)
write_solution_timeout = 0.3
check_proc_delay = 0.001
languages: list = ...
DEBUG = False
source_solution: str = ...

run_as_user_uid_linux = None

test_program = None


def init(config):
    global run_as_user_uid_linux, \
        languages, test_program, source_solution
    run_as_user_uid_linux = config['run_as_user_linux']
    if os.name == 'posix' and run_as_user_uid_linux is not None:
        source_solution = get_source_solution(run_as_user_uid_linux)
    else:
        source_solution = os.path.join(directory, 'source_solution')
    languages = prog_lang.get_languages()
    test_program = TestProgram()


def get_test_program():
    global test_program
    return test_program


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
        if os.name == 'posix' and run_as_user_uid_linux is not None:
            print(f'[Test system] Unix system detected')

        threads_folders = [f'thread_{i + 1}' for i in range(threads)]
        for thread_name in threads_folders:
            source_dir = os.path.join(source_solution, thread_name)
            if not os.path.exists(source_dir):
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
            time.sleep(0.1)
            if self.queue:
                try:
                    solution_id = self._get_from_queue(db_sess)
                except IndexError as e:
                    if DEBUG:
                        print('[Test system] Error in _thread from _get_from_queue:', e)
                else:
                    try:
                        self._run_testing(solution_id, db_sess, source_dir)
                    except Exception as e:
                        print('[Test system] Error in _thread from _run_testing:', e)

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
        path = os.path.join(get_dir(), 'files', 'source_code', f'{solution.source_code.id}.source')
        shutil.copy(path, source)

        try:
            compile_result = lang.compile(os.path.abspath(source))
        except Exception as e:
            error = f'[Test system] Error: abort testing (id={solution.id}) in compile language "{lang.name}", ' \
                    f'exception: "{e}"'
            self.abort_testing(db_sess, solution, error, test_results)
            self.clear_folder(source_dir)

            if DEBUG:
                print(error)
            return

        if not compile_result[0]:
            solution.success = 0
            solution.completed = 1
            solution.state = 11
            solution.state_arg = None

            res = TestResult()
            res.stderr = compile_result[1].decode(lang.encoding)
            test_results.append(res)

            self.write_test_results(solution, test_results)
            self.write_solution(db_sess, solution)
            self.clear_folder(source_dir)
            return

        write_solution_start = self.get_start_time()
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

            proc = None
            try:
                proc = create_process(compile_result[1],
                                      run_as_user_uid_linux,
                                      source_dir)
                proc.stdin.write(stdin.encode(lang.encoding))
                proc.stdin.close()
            except Exception as e:
                if proc is not None:
                    proc.kill()
                error = f'[Test system] Error: abort testing (id={solution.id}) in create_process, ' \
                        f'exception: "{e}"'
                self.abort_testing(db_sess, solution, error, test_results)
                self.clear_folder(source_dir)
                if DEBUG:
                    print(error)
                return

            start_time = self.get_start_time()
            run = True
            if DEBUG:
                prev_time = self.get_start_time()
                count = 0
                summary = 0
            while run:
                if DEBUG:
                    count += 1
                    summary += self.get_delta_time(prev_time)
                    prev_time = self.get_start_time()
                try:
                    current_memory = self.get_memory(proc.pid)
                except psutil.NoSuchProcess:
                    # Из-за параллельного запуска процесс
                    # может отключиться и поднять исключение
                    ...
                if check_proc_delay:
                    time.sleep(check_proc_delay)

                delta = self.get_delta_time(start_time)
                current_time = delta

                if current_time >= problem.time_limit:
                    verdict = 13
                    run = False
                if current_memory >= problem.memory_limit:
                    verdict = 14
                    run = False

                delta = self.get_delta_time(write_solution_start)
                if delta >= write_solution_timeout and new_test:
                    new_test = False
                    write_solution_start = self.get_start_time()
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
                print(f'[Test system] Delta time of proc: {summary / count:.7f}')

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
        self.clear_folder(source_dir)

    def get_queue_length(self):
        return len(self.queue)

    @staticmethod
    def add_solution(source, solution):
        path = os.path.join(get_dir(), 'files', 'source_code',
                            f'{str(solution.source_code.id)}.source')
        with open(path, 'wb') as f:
            f.write(source)

    @staticmethod
    def read_source_code(solution):
        path = os.path.join(get_dir(), 'files', 'source_code',
                            f'{str(solution.source_code.id)}.source')
        with open(path, 'r', encoding='utf8') as f:
            return f.read()

    @staticmethod
    def add_problem(problem, bytes_zip_tests):
        dir_tests = os.path.join(get_dir(), 'files', 'tests', f'{problem.problem_tests.id}')
        try:
            os.mkdir(dir_tests)
        except FileExistsError:
            shutil.rmtree(dir_tests, ignore_errors=True)
            os.mkdir(dir_tests)
        temp_filename = os.path.join(dir_tests, 'temp.zip')
        with open(temp_filename, 'wb') as f:
            f.write(bytes_zip_tests)
        shutil.unpack_archive(temp_filename, dir_tests)
        os.remove(temp_filename)

    @staticmethod
    def write_test_results(solution, test_results: list):
        path = os.path.join(get_dir(), 'files', 'test_result',
                            f'{str(solution.test_result.id)}.json')
        with open(path, 'w') as f:
            json.dump([[x[1] for x in sorted(res.__dict__.items())]
                       for res in test_results], f)

    @staticmethod
    def read_test_results(solution) -> list:
        path = os.path.join(get_dir(), 'files', 'test_result',
                            f'{str(solution.test_result.id)}.json')
        res = []
        try:
            with open(path, 'r') as f:
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
    def write_solution(db_sess, solution, cols=None, commit=True):
        if DEBUG:
            start = TestProgram.get_start_time()
        if cols is None:
            cols = Solution.__table__.columns.keys()
        db_sess.query(Solution).filter(Solution.id == solution.id).update(
            {column: getattr(Solution, column) for column in cols},
            synchronize_session=False
        )
        if commit:
            db_sess.commit()
        if DEBUG:
            print(f'[Test system] --- Time of writing solution ---: '
                  f'{TestProgram.get_delta_time(start):.7f}')

    @staticmethod
    def abort_testing(db_sess, solution, error: str, test_results, commit=True):
        solution.success = 0
        solution.completed = 1
        solution.state = 19
        solution.state_arg = None

        res = TestResult()
        res.stderr = error
        test_results.append(res)

        TestProgram.write_test_results(solution, test_results)
        TestProgram.write_solution(db_sess, solution, commit=commit)

    @staticmethod
    def read_solution(db_sess, id):
        return db_sess.query(Solution).filter(Solution.id == id).first()

    @staticmethod
    def write_problem(db_sess, problem, cols=None, commit=True):
        if cols is None:
            cols = Problem.__table__.columns.keys()
        db_sess.query(Problem).filter(Problem.id == problem.id).update(
            {column: getattr(Problem, column) for column in cols},
            synchronize_session=False
        )
        if commit:
            db_sess.commit()

    @staticmethod
    def read_problem(db_sess, id):
        return db_sess.query(Problem).filter(Problem.id == id).first()

    @staticmethod
    def read_problem_task(problem):
        task = os.path.join(get_dir(), 'files', 'task', f'{problem.task.id}.html')
        with open(task, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def read_tests(problem, n=None):
        path = os.path.join(get_dir(), 'files', 'tests', f'{problem.problem_tests_id}')
        res = []
        k = 0
        for root, dirs, files in os.walk(path):
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
            raise FileNotFoundError(f'[Test system] No tests on "{path}"')
        return res

    @staticmethod
    def check_tests_zip(bytes):
        s1 = set()
        try:
            with ZipFile(BytesIO(bytes)) as z:
                files = z.namelist()
                for name in sorted(files):
                    filename = os.path.split(name)[1]
                    if not filename:
                        continue
                    path_w = os.path.join(os.path.split(name)[0],
                                          os.path.splitext(filename)[0])
                    if os.path.splitext(filename)[1] == '.in':
                        s1.add(path_w)
                    elif os.path.splitext(filename)[1] == '.out':
                        if path_w in s1:
                            s1.remove(path_w)
                        else:
                            print(4)
                            return False
        except zipfile.error as e:
            if DEBUG:
                print(e)
            return False
        if s1:
            print(2)
            return False
        return True

    @staticmethod
    def get_memory(pid):
        """Returns used memory in bytes"""
        process = psutil.Process(pid)
        return process.memory_info().rss

    @staticmethod
    def get_start_time():
        return time.time()

    @staticmethod
    def get_delta_time(start):
        return time.time() - start

    @staticmethod
    def clear_folder(folder, whitelist=()):
        for filename in os.listdir(folder):
            if filename in whitelist:
                continue
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('[Test system] Failed to delete %s. Reason: %s' % (file_path, e))
