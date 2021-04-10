import os
from subprocess import PIPE, Popen


def create_process(cmd: list, uid, white_list: list):
    system = os.name
    if system == 'nt':
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        return proc
    elif system == 'posix':
        # if uid is not None:
        #     proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE,
        #                  preexec_fn=preexec_linux(uid))
        #     return proc
        # proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        # return proc
        firejail = ['firejail', '--noprofile',
                    '--disable-mnt', '--nosound', '--novideo']
        firejail += ['--quiet']
        # for i in white_list:
        #     firejail += [f'--whitelist={i}']
        cmd = firejail + cmd
        proc = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        return proc
    raise ValueError(f'Unrecognized system: "{system}"')


def preexec_linux(uid):
    def decorated():
        os.setuid(uid)

    return decorated
