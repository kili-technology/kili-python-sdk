"""CLI's project create subcommand"""

import json
import os
from typing import Dict, List, Optional, cast
import click
from tabulate import tabulate

from kili.client import Kili
from kili.cli.common_args import Options
from kili.constants import INPUT_TYPE
from kili.queries.project.helpers import get_project_url


@click.command()
@Options.api_key
@Options.endpoint
@click.option('--interface', type=str, required=True,
              help=(
                  "Path pointing to your json interface file "
                  "or the project_id of another Kili project. "
              )
              )
@click.option('--title', type=str, required=True,
              help='Project Title.')
@click.option('--input-type', type=click.Choice(INPUT_TYPE), required=True,
              help='Project input data type. '
              'Please check your license to see which ones you have access to.')
@click.option('--description', type=str, default='',
              help='Project description.')
@Options.tablefmt
# pylint: disable=too-many-arguments
def create_project(api_key: Optional[str],
                   endpoint: Optional[str],
                   input_type,
                   interface: str,
                   title: str,
                   description: str,
                   tablefmt: str,
                   ):
    """Create a Kili project

    If --interface is the project_id of another Kili project,
    it will create a new project with the same json_interface
    (assets will not be copied).

    \b
    !!! Examples
        ```
        kili project create \\
            --interface path/to/interface.json \\
            --input-type TEXT \\
            --title "Invoice annotation project"
        ```
        ```
        kili project create \\
            --interface another_project_id \\
            --input-type TEXT \\
            --title "Invoice annotation project"
        ```
    To build a Kili project interface, please visit: \n
    https://docs.kili-technology.com/docs/customizing-the-interface-through-json-settings
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    if os.path.exists(interface):
        with open(interface, encoding='utf-8') as interface_file:
            json_interface = json.load(interface_file)
    else:
        try:
            json_interface = cast(
                List[Dict],
                kili.projects(project_id=interface, disable_tqdm=True))[
                0]['jsonInterface']
        except:
            # pylint: disable=raise-missing-from
            raise ValueError(
                f'{interface} is not recognized as a json file path nor a Kili project_id')
    result = cast(Dict, kili.create_project(
        input_type=input_type,
        json_interface=json_interface,
        title=title,
        description=description))
    project_id = result['id']

    project_url = get_project_url(project_id, kili.auth.client.endpoint)
    print(
        tabulate(
            [[project_id, project_url]],
            headers=["ID", "URL"],
            tablefmt=tablefmt
        )
    )
