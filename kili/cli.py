"""Kili CLI"""

import os
from typing import Optional, Tuple, List, Dict, cast
import json
import click
from tabulate import tabulate
from typeguard import typechecked
import pandas as pd
import numpy as np
from kili.client import Kili
from kili import __version__
from kili.constants import INPUT_TYPE
from kili.exceptions import NotFound
from kili.mutations.asset.helpers import (
    generate_json_metadata_array, get_file_paths_to_upload)
from kili.mutations.label.helpers import (
    generate_create_predictions_arguments, read_import_label_csv)
from kili.queries.project.helpers import get_project_metadata, get_project_metrics, get_project_url

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

api_key_option = click.option(
    '--api-key', type=str, default=None,
    help=(
        'Your Kili API key. '
    ),
    show_default=(
        '"KILI_API_KEY" environment variable'
    )
)

endpoint_option = click.option(
    '--endpoint', type=str, default=None,
    help=(
        'Kili API Endpoint. '
    ),
    show_default=(
        '"KILI_API_ENDPOINT" environment variable,'
        ' Kili SAAS: "https://cloud.kili-technology.com/api/label/v2/graphql"'
    )
)

tablefmt_option = click.option('--stdout-format', 'tablefmt', type=str, default='plain',
                               help='Defines how the output table is formatted '
                               '(see https://pypi.org/project/tabulate/, default: plain).')


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """Kili Command line Interface

       To get all the available commands, please type: `kili project --help`.
    """


@cli.group(context_settings=CONTEXT_SETTINGS)
def project():
    """Commands to interact with a Kili project"""


@project.command(name="list")
@api_key_option
@endpoint_option
@tablefmt_option
@click.option('--max', 'first', type=int, help='Maximum number of project to display.', default=100)
def list_project(api_key: Optional[str],
                 endpoint: Optional[str],
                 tablefmt: str,
                 first: int):
    """
    List your projects

    \b
    !!! Examples
        ```
        kili project list --max 10 --format pretty
        ```

    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    projects = cast(
        List[Dict],
        kili.projects(
            fields=[
                'title', 'id', 'description', 'numberOfAssets',
                'numberOfRemainingAssets', 'numberOfReviewedAssets'],
            first=first,
            disable_tqdm=True))
    projects = pd.DataFrame(projects)
    projects['progress'] = projects.apply(lambda x: round(
        (1 - x['numberOfRemainingAssets'] / x['numberOfAssets']) * 100, 1)
        if x['numberOfAssets'] != 0 else np.nan, axis=1)

    # Add '%' to PROGRESS if PROGRESS is not nan
    projects['PROGRESS'] = [(str(progress) + '%') if progress >=
                            0 else progress for progress in projects['progress']]
    # If description or title has more than 50 characters, truncate after 47 and add '...'
    projects['DESCRIPTION'] = [(description[:47] + '...').replace('\n', '') if len(description)
                               > 50 else description for description in projects['description']]
    projects['TITLE'] = [(title[:47] + '...') if len(title) >
                         50 else title for title in projects['title']]
    projects['ID'] = projects["id"]

    projects = projects[['TITLE', 'ID', 'PROGRESS', 'DESCRIPTION']]
    print(tabulate(projects, headers='keys', tablefmt=tablefmt,
          showindex=False, colalign=("left", "left", "right", "left")))


@project.command(name='create')
@api_key_option
@endpoint_option
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
@tablefmt_option
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
            json_interface = cast(List[Dict], kili.projects(project_id=interface))[
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


@ project.command(name='import')
@ click.argument('files', type=click.Path(), nargs=-1, required=True)
@api_key_option
@endpoint_option
@click.option('--project-id', type=str, required=True,
              help='Id of the project to import assets into.')
@click.option('--exclude', type=click.Path(exists=True), multiple=True,
              help="Files to exclude from the given files")
@click.option('--frames', 'as_frames', type=bool, default=False, is_flag=True,
              help="Only for a frame project, import videos as frames. "
              "The import time is longer with this option.")
@click.option('--fps', type=int,
              help="Only for a frame project, import videos with a specific frame rate")
@click.option('--verbose', type=bool, is_flag=True, default=False,
              help='Show logs')
@typechecked
# pylint: disable=too-many-arguments
def import_assets(api_key: Optional[str],
                  endpoint: Optional[str],
                  project_id: str,
                  files: Tuple[str, ...],
                  exclude: Optional[Tuple[str, ...]],
                  fps: Optional[int],
                  as_frames: bool,
                  verbose: bool):
    """
    Add assets into a project

    Files can be paths to files or to folders. You can provide several paths separated by spaces.

    \b
    !!! Examples
        ```
        kili project import \\
            dir1/dir2/ dir1/dir3/test1.png \\
            --project-id <project_id> \\
            --exclude dontimport.png
        ```
        ```
        kili project import \\
            dir1/dir3/video.mp4 \\
            --project-id <project_id> \\
            --frames \\
            --fps 24
        ```

    \b
    !!! warning "Unsupported imports"
        Currently, this command does not support:

        - the import of videos from local frames, rich text and time series assets
        - the import of assets with metadata or with a custom external_id

        For such imports, please use the `append_many_to_dataset` method in the Kili SDK.
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    try:
        input_type = cast(List[Dict], kili.projects(project_id,
                                                    disable_tqdm=True,
                                                    fields=['inputType']))[0]['inputType']
    except:
        # pylint: disable=raise-missing-from
        raise NotFound(f'project ID: {project_id}')

    if input_type != 'FRAME' and (fps is not None or as_frames is True):
        illegal_option = 'fps and frames are'
        if not as_frames:
            illegal_option = 'fps is'
        if fps is None:
            illegal_option = 'frames is'
        raise ValueError(f'{illegal_option} only valid for a FRAME project')

    files_to_upload = get_file_paths_to_upload(
        files, input_type, exclude, verbose)
    if len(files_to_upload) == 0:
        raise ValueError(
            'No files to upload. '
            'Check that the paths exist and that the file types are compatible with the project')
    external_ids = [path.split('/')[-1] for path in files_to_upload]
    json_metadata_array = generate_json_metadata_array(
        as_frames, fps, len(files_to_upload), input_type)

    kili.append_many_to_dataset(
        project_id=project_id,
        content_array=files_to_upload,
        external_id_array=external_ids,
        json_metadata_array=json_metadata_array)

    if as_frames:
        print(f'The import of {len(files_to_upload)} files have just started, '
              'you will receive a notification as soon as it is ready.')
    else:
        print(f'{len(files_to_upload)} files have been successfully imported')


@project.command(name="describe")
@click.argument('project_id', type=str, required=True)
@api_key_option
@endpoint_option
def describe_project(api_key: Optional[str],
                     endpoint: Optional[str],
                     project_id: str):
    """Show project description and analytics
    \b
    !!! Examples
        ```
        kili project describe --project-id <project_id>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    projects: List[Dict] = []
    try:
        projects = cast(List[Dict],
                        kili.projects(
            project_id=project_id,
            fields=[
                'title', 'id', 'description', 'numberOfAssets',
                'numberOfRemainingAssets', 'numberOfReviewedAssets',
                'numberOfAssetsWithSkippedLabels',
                'honeypotMark', 'consensusMark',
                'numberOfOpenIssues', 'numberOfSolvedIssues',
                'numberOfOpenQuestions', 'numberOfSolvedQuestions'],
            disable_tqdm=True
        ),
        )
    except:
        # pylint: disable=raise-missing-from
        raise NotFound(f'project ID: {project_id}')
    metadata = get_project_metadata(projects[0], kili.auth.client.endpoint)
    dataset_metrics, quality_metrics = get_project_metrics(projects[0])

    print(tabulate(metadata, tablefmt='plain'), end='\n'*2)
    print('Dataset KPIs', end='\n'+'-'*len('Dataset KPIs')+'\n')
    print(tabulate(dataset_metrics, tablefmt='plain'), end='\n'*2)
    print('Quality KPIs', end='\n'+'-'*len('Quality KPIs')+'\n')
    print(tabulate(quality_metrics, tablefmt='plain'))


@project.command(name='label')
@ click.argument('CSV_path', type=click.Path(exists=True), required=True)
@api_key_option
@endpoint_option
@click.option('--project-id', type=str, required=True,
              help='Id of the project to import labels in')
@click.option('--prediction', 'is_prediction', type=bool, is_flag=True, default=False,
              help='Tells to import labels as predictions, which means that they will appear '
              'as pre-annotations in the Kili interface')
@click.option('--model-name', type=str,
              help='Name of the model that generated predictions, '
              'if labels are sent as predictions')
# pylint: disable=too-many-arguments, too-many-locals
def import_labels(
        csv_path: str,
        api_key: Optional[str],
        endpoint: Optional[str],
        project_id: str,
        is_prediction: bool,
        model_name: str):
    """
    Import labels or predictions

    The labels to import have to be in the Kili format and stored in a json file.
    Labels to import are provided in a CSV file with two columns, separated by a semi-column:

    - `external_id`: external id for which you want to import labels.
    - `json_response_path`: paths to the json files containing the json_response to upload.

    \b
    !!! Examples "CSV file template"
        ```
        external_id;json_response_path
        asset1;./labels/label_asset1.json
        asset2;./labels/label_asset2.json
        ```

    \b
    !!! Examples
        To import default labels:
        ```
        kili project label \\
            path/to/file.csv \\
            --project-id <project_id>
        ```
        To import labels as predictions:
        ```
        kili project label \\
            path/to/file.csv \\
            --project-id <project_id> \\
            --prediction \\
            --model-name YOLO-run-3
        ```

    """
    if is_prediction and model_name is None:
        raise ValueError(
            'When importing labels as prediction, '
            'you must provide a model name with the --model-name option')
    row_dict = read_import_label_csv(csv_path)
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    if kili.count_projects(project_id=project_id) == 0:
        raise NotFound(f'project ID: {project_id}')
    if is_prediction:
        label_paths = [row['json_response_path'] for row in row_dict]
        external_id_array = [row['external_id'] for row in row_dict]
        create_predictions_arguments = generate_create_predictions_arguments(
            label_paths, external_id_array, model_name, project_id)
        kili.create_predictions(**create_predictions_arguments)
        print(f"{len(external_id_array)} labels have been successfully imported")

    else:
        for row in row_dict:
            external_id = row['external_id']
            path = row['json_response_path']
            with open(path, encoding='utf-8') as label_file:
                json_response = json.load(label_file)

            kili.append_to_labels(
                label_asset_external_id=external_id,
                json_response=json_response,
                project_id=project_id)
        print(f"{len(row_dict)} labels have been successfully imported")


def main() -> None:
    """Execute the main function of the command line."""
    cli()


if __name__ == "__main__":
    main()
