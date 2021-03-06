import os
from tempfile import SpooledTemporaryFile as tempfile

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


def test_create_process(uid):
    u_name = pwd.getpwuid(uid).pw_name
    system = os.name
    cmd = ['whoami']
    if system == 'posix':
        # cmd = ['sudo', '-H', '-u', u_name] + cmd
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        return proc
    proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return proc


def create_process(cmd: list, uid, private_folder, stdin, lang):
    system = os.name
    if system == 'posix':
        print(cmd)
        f = tempfile()
        f.write(stdin.encode(lang.encoding))
        f.seek(0)
        proc = Popen(cmd, stdout=PIPE, stdin=f, stderr=PIPE, preexec_fn=preexec(uid))
        f.close()
        return proc

    f = tempfile()
    f.write(stdin.encode(lang.encoding))
    f.seek(0)
    proc = Popen(cmd, stdout=PIPE, stdin=f, stderr=PIPE)
    f.close()
    return proc
    # proc.stdin.write(stdin.encode(lang.encoding))
    # proc.stdin.close()
    # firejail = ['firejail', '--noprofile', '--net=none', '--nosound', '--novideo', '--quiet']
    # for i in range(len(cmd)):
    #     cmd[i] = cmd[i].replace(os.path.join(private_folder, ''), '')
    # cmd = firejail + cmd


def preexec(uid):
    def decorated():
        if uid:
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
    whitelist = ['bash', 'chown']

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
    print(_whitelist)
    for path in _whitelist:
        rights = 'r-x'
        cmd = [setfacl, '-m', f'u:{u_name}:' + rights, path]
        call(cmd)

    print(f'[Test system] Done')
