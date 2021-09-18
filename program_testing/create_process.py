import os

try:
    import pwd
except ImportError:
    pass
from subprocess import PIPE, Popen, check_output, call, CalledProcessError

from program_testing.prog_lang import get_languages


def get_source_solution(uid):
    u_name = pwd.getpwuid(uid).pw_name
    cmd = ['getent', 'passwd', f'{u_name}']
    home = check_output(cmd).decode().split(':')[5]
    source_solution_path = os.path.join(home, 'source_solution')
    if not os.path.exists(source_solution_path):
        os.mkdir(source_solution_path)
    cmd = ['chown', '-R', f'{u_name}:{u_name}', source_solution_path]
    call(cmd)
    return source_solution_path


def create_process(cmd: list, uid, private_folder):
    system = os.name
    if system == 'posix':
        firejail = ['firejail', '--noprofile', '--net=none', '--nosound', '--novideo', '--quiet']
        # for i in range(len(cmd)):
        #     cmd[i] = cmd[i].replace(os.path.join(private_folder, ''), '')
        # cmd = firejail + cmd
        print(' '.join(cmd))
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE,
                     preexec_fn=preexec(uid))
        return proc
    proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return proc


def preexec(uid):
    def decorated():
        os.setuid(uid)

    return decorated


def init_user(uid):
    if not uid or os.name != 'posix':
        return

    forbidden_path = []
    path = os.path.split(check_output(['which', 'ls']).strip())[0]
    for i in check_output([b'ls', path]).split(b'\n'):
        if i:
            try:
                forbidden_path.append(check_output([b'which', i]).strip())
            except Exception:
                continue
    whitelist = ['bash']

    languages = get_languages()
    u_name = pwd.getpwuid(uid).pw_name
    setfacl = check_output(['which', 'setfacl']).strip()
    ans = input(f'[Test system] Init user {u_name} (y/n)? ')
    if ans.strip().lower() != 'y':
        return
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

    print(f'[Test system] Done')
