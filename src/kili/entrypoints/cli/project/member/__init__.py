"""Project member command of Kili CLI."""

import click

from kili.entrypoints.cli.common_args import CONTEXT_SETTINGS
from kili.entrypoints.cli.project.member.add import add_member
from kili.entrypoints.cli.project.member.list_ import list_members
from kili.entrypoints.cli.project.member.remove import remove_member
from kili.entrypoints.cli.project.member.update import update_member


@click.group(context_settings=CONTEXT_SETTINGS)
def member():
    """Commands to interact with Kili project members."""


member.add_command(list_members, name="list")
member.add_command(add_member, name="add")
member.add_command(update_member, name="update")
member.add_command(remove_member, name="rm")
