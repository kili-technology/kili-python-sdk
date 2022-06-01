"""Kili CLI"""

import click
from kili import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """Kili Command line interface."""


def main() -> None:
    """Execute the main function of the command line"""
    cli()


if __name__ == "__main__":
    main()
