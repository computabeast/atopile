import logging

import click
from uvicorn.logging import ColourizedFormatter

from atopile.cli import build, resolve, view

# configure logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.formatter = ColourizedFormatter(fmt="%(levelprefix)s %(name)s %(message)s", use_colors=None)
logging.root.addHandler(stream_handler)

# cli root
@click.group()
def cli():
    pass

cli.add_command(build.build)
cli.add_command(resolve.resolve)
cli.add_command(view.view)

if __name__ == "__main__":
    cli()
