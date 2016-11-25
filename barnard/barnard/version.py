import subprocess
import sys

from . import human


def app_version():
    GIT_DESCRIBE = ["git", "describe", '--match', 'v[0-9]*', "--dirty"]

    human.command_title(GIT_DESCRIBE)
    pro = subprocess.Popen(GIT_DESCRIBE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = pro.communicate()
    if pro.returncode != 0:
        if b'No names found' not in err:
            sys.stderr.buffer.write(err)
            human.error("Can't find out project version")
    else:
        return out.decode('utf-8').strip()

    all_revs = human.command_output(["git", "rev-list", "HEAD"])
    num = all_revs.count(b'\n') - 1
    suffix = all_revs[:7].decode('ascii')
    return 'v0.0.0-{}-g{}'.format(num, suffix)
