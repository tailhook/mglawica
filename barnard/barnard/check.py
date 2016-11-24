import os
import sys
import difflib
import pathlib
from collections import defaultdict

import click
from vagga2lithos.update import updated_config
from vagga2lithos import gen, metadata, lithos, vagga

from .main import main as cli
from .util import write_file
from .infer import get_commands

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
    config = vagga.Config.load('vagga.yaml')
    cmds = dict(get_commands(config))
    by_container = defaultdict(list)
    for name, cmd in cmds.items():
        check_lithos_configs(config, name, cmd, update, verbose)
        by_container[cmd.container].append((name, cmd))
    for cname, commands in by_container.items():
        check_container(config, cname, commands, update, verbose)
    check_barnard(config, by_container.keys(), update, verbose)


def check_lithos_configs(config, name, cmd, update, verbose):
    lithos_file = CONFIG_DIR / ("lithos."+name+".yaml")
    if not lithos_file.exists():
        data = gen.generate_command(config, cmd)
        write_file(lithos_file, data)
    else:
        old_config = lithos.read(lithos_file)
        new_header, new_config = updated_config(old_config, lithos_file,
            config, cmd, verbose=verbose)
        if new_config != old_config:
            if update:
                print("Updates of file:", lithos_file)
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
                # TODO(tailhook) set error code and continue
                sys.exit(7)


def check_container(config, orig_name, cmds, update, verbose):
    cname = '_deploy-' + orig_name
    container = config.containers[cname]
    assert isinstance(container, vagga.Include)
    filename = container.file
    old_container = vagga.load_partial(filename)
    new_container = {
        'setup': [
            vagga.Container(orig_name),
            vagga.EnsureDir('/app'),
        ],
    }
    new_container['setup'].append(vagga.EnsureDir('/config'))
    dirs = set()
    copied = set()
    for cmdname, cmd in cmds:
        for f in getattr(cmd, '_mglawica', {}).get('files', []):
            if '/' in f:
                dir = f[:f.index('/')]
                if dir not in dirs:
                    dirs.add(dir)
                    new_container['setup'].append(
                        vagga.EnsureDir('/app/' + dir))
            if f not in copied:
                new_container['setup'].append(vagga.Copy(
                    source="/work/" + f,
                    path="/app/" + f,
                ))
                copied.add(f)
        new_container['setup'].append(vagga.Copy(
            source="/work/barnard/lithos."+cmdname+".yaml",
            path="/config/lithos."+cmdname+".yaml",
        ))
    if old_container != new_container:
        if verbose:
            if update:
                print("Updating", filename)
            else:
                print("Should update", filename)
        if update:
            data = vagga.dump(new_container)
            write_file(filename, data)
        else:
            # TODO(tailhook) set error code and continue
            sys.exit(7)


def check_barnard(config, containers, update, verbose):
    container = config.containers['barnard']
    assert isinstance(container, vagga.Include)
    filename = container.file
    old_container = vagga.load_partial(filename)
    new_container = {
        'setup': [
            vagga.Unpack([vagga.Include('barnard.yaml')]),
        ],
        'volumes': {},
        'auto-clean': True,
    }
    for cname in containers:
        dir = '/target/' + cname
        new_container['setup'].append(vagga.EnsureDir(dir))
        new_container['volumes'][dir] = vagga.Container(cname)
        data = vagga.dump(new_container)
    if update:
        data = vagga.dump(new_container)
        write_file(filename, data)
    else:
        # TODO(tailhook) set error code and continue
        sys.exit(7)
