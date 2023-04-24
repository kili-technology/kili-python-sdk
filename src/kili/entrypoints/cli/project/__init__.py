"""Project command of Kili CLI."""

import click

from kili.entrypoints.cli.common_args import CONTEXT_SETTINGS
from kili.entrypoints.cli.project.copy import copy_project
from kili.entrypoints.cli.project.create import create_project
from kili.entrypoints.cli.project.describe import describe_project
from kili.entrypoints.cli.project.export import export_labels
from kili.entrypoints.cli.project.import_ import import_assets
from kili.entrypoints.cli.project.label import import_labels
from kili.entrypoints.cli.project.list_ import list_projects
from kili.entrypoints.cli.project.member import member


@click.group(context_settings=CONTEXT_SETTINGS)
def project():
    """Commands to interact with a Kili project."""


project.add_command(create_project, name="create")
project.add_command(describe_project, name="describe")
project.add_command(import_assets, name="import")
project.add_command(import_labels, name="label")
project.add_command(list_projects, name="list")
project.add_command(member, name="member")
project.add_command(export_labels, name="export")
project.add_command(copy_project, name="copy")
