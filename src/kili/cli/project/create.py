"""CLI's project create subcommand"""

import json
from typing import Dict, Optional, cast

import click
from tabulate import tabulate

from kili import services
from kili.cli.common_args import Options
from kili.cli.helpers import get_kili_client
from kili.constants import INPUT_TYPE
from kili.queries.project.helpers import get_project_url


@click.command(name="create")
@Options.api_key
@Options.endpoint
@click.argument("interface", type=click.Path(exists=True), required=False)
@Options.from_project
@click.option("--title", type=str, required=True, help="Project Title.")
@click.option(
    "--input-type",
    type=click.Choice(INPUT_TYPE),
    required=True,
    help="Project input data type. Please check your license to see which ones you have access to.",
)
@click.option("--description", type=str, default="", help="Project description.")
@Options.tablefmt
# pylint: disable=too-many-arguments
def create_project(
    api_key: Optional[str],
    endpoint: Optional[str],
    interface: str,
    project_id_src: str,
    input_type,
    title: str,
    description: str,
    tablefmt: str,
):
    """Create a Kili project

    interface must be a path pointing to your json interface file

    If no interface is provided, --from-project can be used
    to create a new project with the json_interface of another project
    (assets will not be copied).

    \b
    !!! Examples
        ```
        kili project create \\
             path/to/interface.json \\
            --input-type TEXT \\
            --title "Invoice annotation project"
        ```
        ```
        kili project create \\
            --from-project <project_id_src> \\
            --input-type TEXT \\
            --title "Invoice annotation project"
        ```
    To build a Kili project interface, please visit: \n
    https://docs.kili-technology.com/docs/customizing-the-interface-through-json-settings
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    if ((interface is not None) + (project_id_src is not None)) > 1:
        raise ValueError("interface argument and option --from-project are exclusive.")
    if ((interface is not None) + (project_id_src is not None)) == 0:
        raise ValueError("You must use either interface argument or option --from-project")

    if interface is not None:
        with open(interface, encoding="utf-8") as interface_file:
            json_interface = json.load(interface_file)

    elif project_id_src is not None:
        json_interface = services.get_project_field(kili, project_id_src, "jsonInterface")

    result = cast(
        Dict,
        kili.create_project(
            input_type=input_type,
            json_interface=json_interface,
            title=title,
            description=description,
        ),
    )
    project_id = result["id"]

    project_url = get_project_url(project_id, kili.auth.client.endpoint)
    print(tabulate([[project_id, project_url]], headers=["ID", "URL"], tablefmt=tablefmt))
