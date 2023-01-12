"""CLI's project copy subcommand"""

from typing import Optional

import click

from kili import services
from kili.cli.common_args import Options
from kili.cli.helpers import get_kili_client


@click.command(name="copy")
@Options.api_key
@Options.endpoint
@click.argument("from_project_id", type=str, required=True)
@click.option("--title", type=str, required=False, help="New project title.")
@click.option("--description", type=str, required=False, help="New project description.")
@click.option(
    "--with-json-interface/--without-json-interface",
    required=False,
    default=True,
    help="Copy json interface.",
)
@click.option(
    "--with-quality-settings/--without-quality-settings",
    required=False,
    default=True,
    help="Copy quality settings.",
)
@click.option(
    "--with-members/--without-members", required=False, default=True, help="Copy members."
)
@click.option("--with-assets/--without-assets", required=False, default=False, help="Copy assets.")
@click.option("--with-labels/--without-labels", required=False, default=False, help="Copy labels.")
# pylint: disable=too-many-arguments
def copy_project(
    api_key: Optional[str],
    endpoint: Optional[str],
    from_project_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    with_json_interface: bool = True,
    with_quality_settings: bool = True,
    with_members: bool = True,
    with_assets: bool = False,
    with_labels: bool = False,
) -> None:
    """Copy an existing Kili project.

    The copy can include or not the json interface, quality settings, members, assets and labels of
    the source project.

    By default, only the json interface, quality settings and project members are copied.

    If no `title` is provided, the source project title will be used.
    If no description is provided, the description will be set to an empty string.

    Returns the new project id and title once the copy is finished.

    \b
    !!! Examples
        Copy a project and set a new title and new description:
        ```
        kili project copy clbqn56b331234567890l41c0 \\
            --title "New project title" \\
            --description "New project description"
        ```
        Copy the json interface but not the members:
        ```
        kili project copy clbqn56b331234567890l41c0 \\
            --with-json-interface \\
            --without-members
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    new_proj_id = kili.copy_project(
        from_project_id=from_project_id,
        title=title,
        description=description,
        copy_json_interface=with_json_interface,
        copy_quality_settings=with_quality_settings,
        copy_members=with_members,
        copy_assets=with_assets,
        copy_labels=with_labels,
    )
    title = services.get_project_field(kili, new_proj_id, "title")
    print(f'Project copied successfully. New project id: "{new_proj_id}", with title: "{title}"')
