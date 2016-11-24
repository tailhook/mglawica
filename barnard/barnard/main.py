import click

@click.group()
def main():
    pass


from . import check
from . import deploy


