import os
import random
from subprocess import Popen, PIPE

directory = os.path.dirname(__file__)
languages = None


def init(config):
    global languages
    languages = {i.code_name: i for i in map(
        lambda x: x(),
        [
            ProgLangCPP,
            ProgLangPascalABCNet,
            ProgLangPython,
            ProgLangPyPy,
            ProgLangJava,
            ProgLangC,
        ])}

    config = config
    encoding = config['encoding']
    for i in languages.values():
        i: ProgLang
        i.compiler = config['languages'][i.code_name]
        i.encoding = encoding


def get_languages():
    return languages


class ProgLang:
    def __init__(self, name, code_name, extension, encoding='cp866'):
        self.name = name
        self.code_name = code_name.lower().replace(' ', '')
        self.extension = extension
        self.encoding = encoding
        self.compiler = []

    def compile(self, source):
        """Returns (0, *error*) if not compiled, else (1, *command to execute*)"""
        ...

    def check_correct(self):
        try:
            proc = Popen([self.compiler[0]], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            comm = proc.communicate()
            return True
        except FileNotFoundError:
            return False


def get_rpython(source):
    allowed_imports = ['random', 'itertools', 'functools', 'gc']

    # Create RestrictedPython
    d, name = os.path.split(source)
    path = os.path.join(d, os.path.splitext(name)[0] + f'_{random.randint(100000, 1000000)}.py')
    with open(source, 'r', encoding='utf-8') as f:
        code = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        rpython = f'''
import importlib

def secure_importer(name, globals=None, locals=None, fromlist=(), level=0):
    # not exactly a good verification layer
    frommodule = globals['__name__'] if globals else None
    if name not in {allowed_imports}:
        raise ImportError("module '%s' is disabled."%name)

    return importlib.__import__(name, globals, locals, fromlist, level)

__builtins__.__dict__['__import__'] = secure_importer

source_code = """
{code}
"""
byte_code = compile(
    source_code,
    filename='<inline>',
    mode='exec'
)
exec(byte_code, globals(), None)

'''.strip()
        f.write(rpython)
    return path


class ProgLangPython(ProgLang):
    def __init__(self):
        super().__init__('Python 3.7.3', 'python', 'py')

    def compile(self, source):
        cmd = [self.compiler[0], '-I', '-m', 'py_compile', source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [self.compiler[0], get_rpython(source)]


class ProgLangPyPy(ProgLang):
    def __init__(self):
        super().__init__('PyPy 7.0.0 (GCC 8.2.0)', 'pypy', 'py')

    def compile(self, source):
        cmd = [self.compiler[0], '-I', '-m', 'py_compile', source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [self.compiler[0], get_rpython(source)]


class ProgLangPascalABCNet(ProgLang):
    def __init__(self):
        super().__init__('PascalABC.NET v3.8.1.2985', 'pabcnet', 'pas')

    def compile(self, source):
        d, name = os.path.split(source)
        path = os.path.join(d, os.path.splitext(name)[0] + '.exe')
        cmd = [self.compiler[0], self.compiler[1], source]
        print(cmd)
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[0]
            return 0, err
        return 1, [path]


class ProgLangCPP(ProgLang):
    def __init__(self):
        super().__init__('C++ 8.3.0', 'c++', 'cpp')

    def compile(self, source):
        d, name = os.path.split(source)
        path = os.path.join(d, os.path.splitext(name)[0] + '.exe')
        cmd = [self.compiler[0], '-Wall', '-static', '-std=gnu++17', '-s', '-O2', source, '-o', path, '-lm']
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [path]


class ProgLangC(ProgLang):
    def __init__(self):
        super().__init__('GCC 8.3.0', 'c', 'c')

    def compile(self, source):
        d, name = os.path.split(source)
        path = os.path.join(d, os.path.splitext(name)[0] + '.exe')
        cmd = [self.compiler[0], '-Wall', '-static', '-std=gnu17', '-s', '-O2', source, '-o', path, '-lm']
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [path]


class ProgLangCS(ProgLang):
    def __init__(self):
        super().__init__('C#', 'c#', 'cs')

    def compile(self, source):
        d, name = os.path.split(source)
        path = os.path.join(d, os.path.splitext(name)[0] + '.exe')
        cmd = [self.compiler[0], '-optimize', f'-out:{path}', source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[0]
            return 0, err
        return 1, self.compiler[1:] + [path]


class ProgLangJava(ProgLang):
    def __init__(self):
        super().__init__('Java (jdk 11.0.11)', 'java', 'java')

    def compile(self, source):
        d, name = os.path.split(source)
        cmd = [self.compiler[0], source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [self.compiler[1], '-classpath', d, 'program']
