import os
import pathlib

from .main import main as cli

CONFIG_DIR = pathlib.Path('/work/barnard')


@cli.command()
def check():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir()
    if not (CONFIG_DIR / "lithos.yaml").exists():
        from vagga2lithos import gen
        gen.generate(input='vagga.yaml', vagga_command='run')
    else:
        from vagga2lithos import update
        gen.check(['vagga.yaml', 'run', CONFIG_DIR / "lithos.yaml"],
            verbose=True)
