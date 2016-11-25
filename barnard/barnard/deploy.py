import os
import time
import json

import click
import pprint
import requests

from .main import main as cli
from vagga2lithos import vagga
from .infer import get_commands
from .version import app_version
from . import containers, human


@cli.command()
@click.option('-n', '--dry-run/--do-job', default=False,
    help="Don't run destructive commands")
@click.option('--override-version-number', default=None,
    help="Use this version number for deployment. Usually we use \
          `git describe --dirty --match 'v[0-9]*'` for version number. \
          But if you have different versioning scheme or your `vagga.yaml` \
          not in the root of the repository use this option.")
def deploy(dry_run, override_version_number):
    try:
        _deploy(dry_run, override_version_number)
    except Exception as e:
        human.error(e)

def _deploy(dry_run, override_version_number):
    ids = containers.discover()
    config = vagga.Config.load('vagga.yaml')
    cmds = dict(get_commands(config))

    role_names = [c._mglawica['name'] for c in cmds.values()]
    role = role_names[0]
    if not all(r == role for r in role_names):
        raise RuntimeError("Can't manage projects with multiple roles yet")

    if override_version_number is not None:
        version = override_version_number
    else:
        version = app_version()

    human.value("Application name", role)
    human.value("Version", version)

    daemons = {}
    for cname, cmd in cmds.items():
        data = {
            'image': ids['_deploy-' + cmd.container],
            'config': '/config/lithos.'+cname+'.yaml',
        }
        if 'port' in cmd._mglawica:
            data['http-host'] = cmd._mglawica['name']
            data['port'] = cmd._mglawica['port']
        daemons[cname] = data
    human.pprint('Deployment config', daemons)

    data = json.dumps({
        "daemons": daemons,
        "timestamp": str(time.time()),
    }, indent=2)

    if dry_run:
        # TODO(tailhook) add more checks show rsync commands
        print("All checks complete. Version", version, "is ready to go")
        return

    with requests.session() as sess:

        for name, uniq in ids.items():
            base = 'http://172.24.0.1/~~/lithos/images/' + role + '/'
            dest = base + uniq + '/'
            if sess.get(dest).raw.status == 200:
                print("Image {} is already uploaded".format(uniq))
            else:
                tmp = base + name + '.tmp/'
                tmp2 = base + name + '.{}.tmp/'.format(time.time())
                sess.request('MOVE', tmp,
                    headers={
                        'Host': 'internal',
                        'Destination': tmp2.replace('172.24.0.1', 'internal'),
                    }).raw.read()
                sess.request('DELETE', tmp2,
                             headers={'Host': 'internal'}).raw.read()
                sess.request('MKCOL', base,
                             headers={'Host': 'internal'}).raw.read()

                human.command(["rsync", "-rlp",
                    "/target/{}/".format(name),
                    "rsync://172.24.0.1/images/{}/{}.tmp".format(role, name),
                ], dry_run)

                sess.request('MOVE', tmp,
                    headers={
                        'Host': 'internal',
                        'Destination': dest.replace('172.24.0.1', 'internal'),
                    }).raw.read()

            sess.put(
                'http://172.24.0.1/~~/verwalter/runtime/{}/{}.json'
                    .format(role, version),
                headers={'Host': 'internal'},
                data=data).raw.read()

        print("Done", version, "App should be restarted shortly...")

        meta = sess.get(
            'http://172.24.0.1/~~/verwalter/runtime/metadata.json',
            headers={'Host': 'internal'}).json()

        for dname, daemon in daemons.items():
            port = daemon.get('port')
            if port:
                print("Service", dname, "is accessible at:")
                print("http://h1.mglawica.org:{}/ (VPN only)".format(port))
                for host in meta.get('base_hosts'):
                    if 'mglawica.org' in host:
                        print("http://{}.{}/ (VPN only)".format(role, host))
                    else:
                        print("http://{}.{}/".format(role, host))

