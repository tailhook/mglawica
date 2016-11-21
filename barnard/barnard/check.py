import os
import sys
import difflib
import pathlib

import click
from vagga2lithos.vagga import Config as Vagga
from vagga2lithos.update import updated_config
from vagga2lithos import gen, metadata, lithos

from .main import main as cli
from .util import write_file

CONFIG_DIR = pathlib.Path('/work/barnard')


@cli.command()
@click.option('-u', '--update/--no-update', default=False,
    help='Update files')
@click.option('-v', '--verbose/--quiet', default=False,
    help='Print diagnostic messsages')
def check(update, verbose):
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir()
    # TODO(tailhook) check if barnard is itself well-configured
    vagga = Vagga.load('vagga.yaml')
    cmd = vagga.commands.get('_deploy-run', vagga.commands.get('run'))
    lithos_file = CONFIG_DIR / "lithos.yaml"
    if not lithos_file.exists():
        data = gen.generate_command(vagga, cmd)
        write_file(lithos_file, data)
    else:
        old_config = lithos.read(lithos_file)
        new_header, new_config = updated_config(old_config, lithos_file,
            vagga, cmd, verbose=verbose)
        if new_config != old_config:
            if update:
                print("Update to the file:", lithos_file)
            else:
                print("Proposed changes to the file:", lithos_file)
            old = lithos.dump(old_config)
            new = lithos.dump(new_config)
            print('\n'.join(difflib.ndiff(old.splitlines(),
                                          new.splitlines())))
            if update:
                d = metadata.dump_header(new_header) + lithos.dump(new_config)
                write_file(lithos_file, d)
            else:
                sys.exit(1)
