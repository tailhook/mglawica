import os
import sys
import time
import shlex
import subprocess
import traceback
from pprint import pformat


def exception(error, message, fatal=True):
    if os.environ.get("BARNARD_EXCEPTIONS"):
        traceback.print_exception(None, error, error.__traceback__,
            file=sys.stderr)
    else:
        print("Exception: {0.__class__.__name__}: {0}".format(error),
            file=sys.stderr)
    print("FATAL ERROR:" if fatal else "ERROR:", message, file=sys.stderr)
    sys.stderr.flush()
    if fatal:
        exit(1)


def error(message):
    print("FATAL ERROR:", message, file=sys.stderr)
    sys.stderr.flush()
    exit(1)


def value(key, value):
    print("{}: {}".format(key, value), file=sys.stderr)
    sys.stderr.flush()


def pprint(key, value):
    print("{}: {}".format(key,
        pformat(value).replace('\n', '\n  ' + ' '*len(key))),
        file=sys.stderr)
    sys.stderr.flush()


def operation(message):
    print(message, end='\r', file=sys.stderr)
    sys.stderr.flush()


def title(message):
    print(message, file=sys.stderr)
    sys.stderr.flush()


def bold(message):
    print("*****", message, "*****", file=sys.stderr)
    sys.stderr.flush()


def warning(message):
    print("WARNING:", message, file=sys.stderr)
    sys.stderr.flush()


def done(version, dry_run):
    if dry_run:
        print("`"*5, "DONE (dry_run)", "version:", version, "`"*5,
            file=sys.stderr)
    else:
        print("-"*5, "DONE", "version:", version, "-"*5, file=sys.stderr)
    sys.stderr.flush()


def auxiliary(text):
    print("    => {}".format(text), file=sys.stderr)
    sys.stderr.flush()


def command_output(cmdline, **kwargs):
    command_title(cmdline)
    return subprocess.check_output(cmdline, **kwargs)


def command_title(cmdline):
    auxiliary(' '.join(map(shlex.quote, cmdline)))


def command(cmdline, dry_run=False, **kwargs):
    auxiliary(' '.join(map(shlex.quote, cmdline)))
    if not dry_run:
        start_time = time.time()
        subprocess.check_call(cmdline, **kwargs)
        duration = time.time() - start_time
        if duration > 5.0:
            print("    .. done in {:.0f} sec".format(duration),
                  file=sys.stderr)


def print_err(e, prefix=''):
    for k, v in e.items():
        if isinstance(v, dict):
            print_err(v, prefix + k + '.')
        else:
            print(prefix + str(k) + ':', v, file=sys.stderr)


def dataerror(message, e):
    print("FATAL ERROR:", message + ":", file=sys.stderr)
    print_err(e.as_dict(), prefix='  ')
    sys.stderr.flush()
    exit(1)
