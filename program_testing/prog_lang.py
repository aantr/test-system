import os
from subprocess import Popen, PIPE

directory = os.path.dirname(__file__)
languages = None


def init(config):
    global languages
    languages = {i.code_name: i for i in map(
        lambda x: x(),
        [
            ProgLangPython, ProgLangPascalABCNET,
            ProgLangCPP, ProgLangJava, ProgLangC, ProgLangCS
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


class ProgLangPython(ProgLang):
    def __init__(self):
        super().__init__('Python', 'python', 'py')

    def compile(self, source):
        cmd = [self.compiler[0], '-I', '-m', 'py_compile', source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [self.compiler[0], source]


class ProgLangPascalABCNET(ProgLang):
    def __init__(self):
        super().__init__('PascalABC.NET', 'pascalabc.net', 'pas')

    def compile(self, source):
        cmd = [self.compiler[0], source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[0]
            return 0, err
        d, name = os.path.split(source)
        path = os.path.join(d, os.path.splitext(name)[0] + '.exe')
        return 1, [path]


class ProgLangCPP(ProgLang):
    def __init__(self):
        super().__init__('C++', 'c++', 'cpp')

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
        super().__init__('C', 'c', 'c')

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
        return 1, [path]


class ProgLangJava(ProgLang):
    def __init__(self):
        super().__init__('Java', 'java', 'java')

    def compile(self, source):
        d, name = os.path.split(source)
        cmd = [self.compiler[0], source]
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        comm = proc.communicate()
        if proc.poll():
            err = comm[1]
            return 0, err
        return 1, [self.compiler[1], '-classpath', d, 'program']
