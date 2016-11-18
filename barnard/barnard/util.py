import os


def write_file(path, data):
    path = str(path)
    with open(path + '.tmp', 'wt') as f:
        f.write(data)
    os.rename(path + '.tmp', path)
