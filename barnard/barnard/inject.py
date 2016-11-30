import re
import os
import pathlib

import yaml
import click
from yaml import MappingNode
from vagga2lithos import vagga

from . import human
from .util import write_file
from .main import main as cli


EMPTY_LINE = re.compile("^\w*(?:#.*)?$")

COMMAND = """\
!Command
description: Run barnard (a container deployment tool)
container: barnard
run:
- barnard
"""

CONTAINER = """\
auto-clean: true
setup:
- !*Unpack [!*Include "barnard.yaml"]
- !EnsureDir "/target/py"
volumes:
  /target/py: !Container "py"
"""


def error(e, *args):
    human.error("invalid vagga.yaml: " + e.format(*args))


@cli.command()
@click.option('-f', '--input', default='vagga.yaml',
    help='The vagga.yaml file to read')
def inject(input):
    with open(input) as f:
        text = f.read()
        root = yaml.compose(text)
        lines = text.splitlines()
    if not isinstance(root, MappingNode):
        error("root node must be mapping, not {}", type(root))
    if root.flow_style:
        error("flow style (using braces) is not supported in root of config")

    containers_line = None
    containers_indent = None
    commands_line = None
    commands_indent = None

    for (key, value) in root.value:
        if key.value == 'containers':
            if not value.value:
                error("No containers found")
            subkey = value.value[0][0]
            containers_indent = subkey.start_mark.column
            containers_line = value.end_mark.line
            while EMPTY_LINE.match(lines[containers_line-1]):
                containers_line -= 1
        if key.value == 'commands':
            if not value.value:
                error("No commands found")
            subkey = value.value[0][0]
            commands_indent = subkey.start_mark.column
            commands_line = value.end_mark.line
            while EMPTY_LINE.match(lines[commands_line-1]):
                commands_line -= 1

    if commands_line is None:
        error("No commands found")

    if containers_line is None:
        error("No containers found")

    cnt_text = (" "*containers_indent +
        'barnard: !*Include "vagga/barnard.container.yaml"')
    cmd_text = (" "*commands_indent +
        'barnard: !*Include "vagga/barnard.command.yaml"')

    if commands_line < containers_line:
        lines.insert(containers_line, cnt_text)
        lines.insert(commands_line, cmd_text)
    else:
        lines.insert(commands_line, cmd_text)
        lines.insert(containers_line, cnt_text)

    try:
        config = vagga.Config.load('vagga.yaml')
        barnard = config.containers['barnard']
    except Exception as e:
        human.exception(e,
            "we expect barnard to be present in vagga.yaml in current dir")

    barnard_cfg = vagga.dump(barnard['setup'])

    projdir = pathlib.Path(input)
    dir = projdir.parent / 'vagga'
    if not dir.exists():
        os.makedirs(str(dir))
    write_file(dir / 'barnard.container.yaml', CONTAINER)
    write_file(dir / 'barnard.command.yaml', COMMAND)
    write_file(dir / 'barnard.yaml', barnard_cfg)

    write_file(input, '\n'.join(lines) + '\n')


