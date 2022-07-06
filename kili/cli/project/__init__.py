import click

from kili.cli.common_args import CONTEXT_SETTINGS

from kili.cli import project

from kili.cli.project.create import create
from kili.cli.project.describe import describe
from kili.cli.project.import_ import import_
from kili.cli.project.label import label
from kili.cli.project.list_ import list_


@click.group(context_settings=CONTEXT_SETTINGS)
def project():
    """Commands to interact with a Kili project"""


project.add_command(create, name="create")
project.add_command(describe, name="describe")
project.add_command(import_, name="import")
project.add_command(label, name="label")
project.add_command(list_, name="list")
