"""CLI's project upload_plugin subcommand"""
import click

from pathlib import Path
from typing import Dict, List, Optional, cast

from typeguard import typechecked

from kili.cli.common_args import Arguments, Options
from kili.client import Kili
from kili.exceptions import NotFound


@click.command(name="upload_plugin")
@Arguments.file_path
@Options.api_key
@Options.endpoint
@Options.project_id
@Options.script_name
@Options.verbose
@typechecked
# pylint: disable=too-many-arguments
def upload_plugin(
    api_key: Optional[str],
    endpoint: Optional[str],
    project_id: str,
    file_path: str,
    script_name: Optional[str],
    verbose: bool,
):
    """
    Add a plugin to a project

    file_path is the path to your file.

    \b
    !!! Examples
        ```
        kili project upload_plugin \\
            main.py \\
            --project-id <project_id>
        ```
    \b

    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    try:
        title = cast(List[Dict], kili.projects(project_id, disable_tqdm=True, fields=["title"]))[0][
            "title"
        ]

        print(f"Found project: {title}")
    except:
        # pylint: disable=raise-missing-from
        raise NotFound(f"project ID: {project_id}")
    path = Path(file_path)
    if not path.is_file():
        raise ValueError(
            "No files to upload. "
            "Check that the path exists and file types are compatible with the project"
        )

    kili.upload_plugin(
        project_id=project_id, file_path=file_path, script_name=script_name, verbose=verbose
    )

    print(f"{file_path} script has been successfully uploaded")
