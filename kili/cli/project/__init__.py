import click

from kili.cli.common_args import CONTEXT_SETTINGS

from kili.cli.project.create import create_project
from kili.cli.project.describe import describe_project
from kili.cli.project.import_asset import import_assets
from kili.cli.project.import_label import import_labels
from kili.cli.project.list import list_project


@click.group(context_settings=CONTEXT_SETTINGS)
def project_group():
    """Commands to interact with a Kili project"""


project_group.add_command(create_project, name="create")
project_group.add_command(describe_project, name="describe")
project_group.add_command(import_assets, name="import")
project_group.add_command(import_labels, name="label")
project_group.add_command(list_project, name="list")
