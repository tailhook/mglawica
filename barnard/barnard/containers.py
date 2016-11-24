def discover():
    containers = {}
    with open('/proc/self/mountinfo', encoding='ascii') as f:
        for line in f:
            _, _, _, source, dest, *_ = line.split()
            if not dest.startswith("/target/"):
                continue
            name = dest[len("/target/"):]
            assert '/' not in name, name
            _, ver, root = source.rsplit('/', 2)
            assert root == 'root', root
            containers[name] = ver
    return containers
