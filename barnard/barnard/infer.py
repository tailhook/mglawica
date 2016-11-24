def get_commands(config):
    for (cname, cmd) in config.commands.items():
        if hasattr(cmd, '_mglawica'):
            if cname == 'run':
                cname = 'main'
            yield cname, cmd
        if getattr(cmd, 'children', None):
            for (cname2, cmd) in cmd.children.items():
                if hasattr(cmd, '_mglawica'):
                    if cname == 'run':
                        yield cname2, cmd
                    else:
                        yield cname + '-' + cname2, cmd
