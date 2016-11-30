import re
import os
import pathlib
import readline

import yaml
import click
from yaml import MappingNode
from vagga2lithos import vagga

from . import human
from .util import write_file
from .main import main as cli

ROLE_RE = re.compile("^[a-zA-Z][a-zA-Z0-9-]*$")


def error(e, *args):
    human.error("invalid vagga.yaml: " + e.format(*args))


@cli.command()
@click.option('-f', '--input', default='vagga.yaml',
    help='The vagga.yaml file to read')
def bootstrap(input):
    with open(input) as f:
        text = f.read()
        root = yaml.compose(text)
        lines = text.splitlines()
    if not isinstance(root, MappingNode):
        error("root node must be mapping, not {}", type(root))
    if root.flow_style:
        error("flow style (using braces) is not supported in root of config")

    cmds = {}
    for (key, value) in root.value:
        if key.value == 'commands':
            for pair in value.value:
                cmds[pair[0].value] = pair

    cmd, config = ask_questions(cmds)

    print("Fine. Your config is:")
    print("")
    exlines = yaml.dump({'commands': {cmd: config}}).splitlines()
    exlines[1] += ' !Command'
    exlines.insert(2, "    # .. command config ...")
    print('\n'.join(exlines))
    print("")
    print("We'll try to put it in file, but this sometimes fails")

    destcmd = cmds[cmd]
    for key, val in destcmd[1].value:
        if key.value == 'run':
            run_line = key.start_mark.line
            run_indent = key.start_mark.column
            break
    else:
        human.error("Can't find `run` in your command. "
                    "Supervise commands are not supported yet")

    indent = ' '*run_indent
    data = yaml.dump(config).splitlines()
    lines[run_line:run_line] = [indent + line for line in data]
    write_file(input, '\n'.join(lines))


def ask_questions(cmds):
    print("Okay. We are going to add some small but important metadata")
    print("to your vagga.yaml file.")
    print("")
    print("Don't be too cautious here, you can edit it later")
    print("directly in vagga.yaml")
    print("")

    print("Available commands:", ', '.join(cmds))
    while True:
        cmd = input("Which command you want to deploy: ").strip()
        if cmd not in cmds:
            print("No such command:", cmd)
        else:
            break
    print("Got it. Command:", repr(cmd))

    print("")
    print("You need some name for the program that is global to your cluster")
    while True:
        role = input("Role name: ").strip()
        if not ROLE_RE.match(role):
            print("Sorry, only alphanumeric and dash allowed")
        else:
            break
    print(repr(cmd), "is good name. Just few things left.")

    print("")
    print("You need a free port on your host system. Different services must")
    print("allocate different ports. Good value is somewhere ")
    print("in the range 10000-20000")
    while True:
        port = input("Port: ").strip()
        try:
            port = int(port)
        except ValueError:
            print("Bad port value")
            continue
        if port > 65535:
            print("Port too large")
            continue
        if port < 1024:
            print("We can't use privileged ports yet")
            continue
        break

    print("")
    print("The last step is to choose which files are going to be deployed.")
    print("Container is always deployed, but probably you will need some")
    print("files from your working directory")
    print("")
    files = [x for x in os.listdir(".") if not x.startswith('.')]
    if len(files) > 20:
        print("You have", len(files), "and directories in your workdir")
    else:
        print("Your directory list:", " ".join(files))
    print("")
    print("Enter space separated list of files and directories. Vagga will")
    print("version them properly as part of container. You can edit the list")
    print("later")
    files = input("Files: ").split()
    config = {
        '_mglawica': {
            'role': role,
            'port': port,
            'files': files,
        }
    }
    return cmd, config


