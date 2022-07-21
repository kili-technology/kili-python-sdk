"""Project member command of Kili CLI"""

import click

from kili.cli.common_args import CONTEXT_SETTINGS
from kili.cli.project.member.list_ import list_members
from kili.cli.project.member.add import add_member


@click.group(context_settings=CONTEXT_SETTINGS)
def member():
    """Commands to interact with Kili project members"""


member.add_command(list_members, name="list")
member.add_command(add_member, name="add")
