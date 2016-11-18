import os
import pathlib
from vagga2lithos.vagga import Config as Vagga
from vagga2lithos import gen

from .main import main as cli
from .util import write_file

CONFIG_DIR = pathlib.Path('/work/barnard')


@cli.command()
def check():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir()
    # TODO(tailhook) check if barnard is itself well-configured
    vagga = Vagga.load('vagga.yaml')
    cmd = vagga.commands.get('_deploy-run', vagga.commands.get('run'))
    lithos = CONFIG_DIR / "lithos.yaml"
    if not lithos.exists():
        data = gen.generate_command(vagga, cmd)
        write_file(lithos, data)
    else:
        from vagga2lithos import update
        gen.check(['vagga.yaml', 'run', CONFIG_DIR / "lithos.yaml"],
            verbose=True)
