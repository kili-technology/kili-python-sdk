"""Kili CLI"""
import click
from kili.cli.common_args import CONTEXT_SETTINGS

from kili import __version__


from kili.cli.project.create import create_project as create
from kili.cli.project.describe import describe_project as describe
from kili.cli.project.import_asset import import_assets
from kili.cli.project.import_label import import_labels
from kili.cli.project.list import list_project


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """Kili Command line Interface

       To get all the available commands, please type: `kili project --help`.
    """


@cli.group(context_settings=CONTEXT_SETTINGS)
def project():
    """Commands to interact with a Kili project"""


project.add_command(create, name="create")
project.add_command(describe, name="describe")
project.add_command(import_assets, name="import")
project.add_command(import_labels, name="label")
project.add_command(list_project, name="list")


@cli.group(context_settings=CONTEXT_SETTINGS)
def organization():
    """Commands to interact with a Kili oragnization"""


def main() -> None:
    """Execute the main function of the command line."""
    cli()


if __name__ == "__main__":
    main()
