from cgroups import Cgroup
from cgroups.user import create_user_cgroups
import os
import subprocess
# Устанавливаем для пользователя директории cgroup
user = os.getlogin()
create_user_cgroups(user)
# Создаем cgroup и устанавливаем лимиты на cpu и память
cg = Cgroup(name)
cg.set_cpu_limit(50)  # TODO : получать эти значения из опций командной строки
cg.set_memory_limit(500)
cg.


# Создадим функцию добавления процесса в cgroup
def in_cgroup():
    pid = os.getpid()
    cg = Cgroup(name)
    for env in env_vars:
        os.putenv(*env.split('=', 1))
    # add process to cgroup
    cg.add(pid)
    os.chroot(layer_dir)
    if working_dir != '':
        log.info("Setting working directory to %s" % working_dir)
        os.chdir(working_dir)


cmd= []
process = subprocess.Popen(cmd, preexec_fn=in_cgroup, shell=True)
process.wait()
print(process.stdout)
