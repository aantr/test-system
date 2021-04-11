import os
import pwd
from subprocess import PIPE, Popen, check_output, call, CalledProcessError

from program_testing.prog_lang import get_languages

forbidden_path = []
path = os.path.split(check_output(['which', 'ls']).strip())[0]
for i in check_output([b'ls', path]).split(b'\n'):
    if i:
        try:
            forbidden_path.append(check_output([b'which', i]).strip())
        except Exception:
            continue
whitelist = ['bash']


def create_process(cmd: list, uid):
    system = os.name
    if system == 'nt':
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        return proc
    elif system == 'posix':
        firejail = ['firejail', '--noprofile', '--net=none', '--noroot',
                    '--disable-mnt', '--nosound', '--novideo']
        firejail = []
        cmd = firejail + cmd
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE,
                     preexec_fn=preexec_linux(uid))
        return proc
    raise ValueError(f'Unrecognized system: "{system}"')


def preexec_linux(uid):
    def decorated():
        os.setuid(uid)

    return decorated


def init_user(uid):
    if not uid or os.name != 'posix':
        return
    languages = get_languages()
    u_name = pwd.getpwuid(uid).pw_name
    setfacl = check_output(['which', 'setfacl']).strip()
    print(f'[Test system] Init user {u_name}')
    _whitelist = set()
    for i in whitelist:
        path = check_output(['which', i]).strip()
        _whitelist.add(path)

    for lang in languages.values():
        for command in lang.compiler:
            try:
                path = check_output(['which', command]).strip()
            except CalledProcessError:
                print(f'[Test system] Cannot find "{command}"')
                continue
            _whitelist.add(path)

    for path in forbidden_path:
        rights = '---'
        cmd = [setfacl, '-m', f'u:{u_name}:' + rights, path]
        call(cmd)

    for path in _whitelist:
        rights = 'r-x'
        cmd = [setfacl, '-m', f'u:{u_name}:' + rights, path]
        call(cmd)
