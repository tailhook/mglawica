import os
import time
import json

import click
import pprint

from .main import main as cli
from vagga2lithos import vagga
from .infer import get_commands
from . import containers, human


@cli.command()
@click.option('-n', '--dry-run/--do-job', default=False,
    help="Don't run destructive commands")
def deploy(dry_run):
    ids = containers.discover()
    config = vagga.Config.load('vagga.yaml')
    cmds = dict(get_commands(config))

    role_names = [c._mglawica['name'] for c in cmds.values()]
    role = role_names[0]
    if not all(r == role for r in role_names):
        raise RuntimeError("Can't manage projects with multiple roles yet")

    os.mkdir('/tmp/config')
    with open('/tmp/config/daemons.json', 'wt') as f:
        daemons = {}
        for cname, cmd in cmds.items():
            data = {
                'image': ids['_deploy-' + cmd.container],
                'config': '/config/lithos.'+cname+'.yaml',
            }
            if 'port' in cmd._mglawica:
                data['port'] = cmd._mglawica['port']
            daemons[cname] = data
        human.pprint('Deployment config', daemons)
        json.dump(daemons, f, indent=2)

    with open("/tmp/config/timestamp.txt", "wt") as f:
        f.write(str(time.time()))

    # this is sorta remote mkdir
    os.mkdir("/tmp/empty")
    for server in self.image_servers:
        human.command(["rsync", "-rlp",
            "/tmp/empty/",
            "rsync://172.24.0.1/images",
        ], dry_run)
    os.rmdir('/tmp/empty')

    for name, uniq in ids:
