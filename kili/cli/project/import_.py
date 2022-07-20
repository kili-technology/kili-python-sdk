"""CLI's project import subcommand"""

from typing import Dict, Optional, List, Tuple, cast
import click
from typeguard import typechecked
from kili.cli.common_args import Options, from_csv
from kili.client import Kili
from kili.exceptions import NotFound
from kili.mutations.asset.helpers import generate_json_metadata_array, get_file_paths_to_upload
from kili.mutations.label.helpers import read_import_label_csv


@click.command()
@click.argument('files', type=click.Path(), nargs=-1, required=False)
@Options.api_key
@Options.endpoint
@Options.project_id
@from_csv(False, ['external_id', 'content'], [])
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
                  csv_path: Optional[str],
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
            --project-id <project_id>
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

    if input_type not in ('FRAME', 'VIDEO') and (fps is not None or as_frames is True):
        illegal_option = 'fps and frames are'
        if not as_frames:
            illegal_option = 'fps is'
        if fps is None:
            illegal_option = 'frames is'
        raise ValueError(f'{illegal_option} only valid for a VIDEO project')

    if ((files is not None) + (csv_path is not None)) > 1:
        raise ValueError(
            'files arguments and option --from-csv are exclusive.')
    if ((files is not None) + (csv_path is not None)) == 0:
        raise ValueError(
            'You must use either file arguments or option --from-csv')

    if files is not None:
        files_to_upload = get_file_paths_to_upload(
            files, input_type, verbose)
        if len(files_to_upload) == 0:
            raise ValueError(
                'No files to upload. '
                'Check that the paths exist and file types are compatible with the project')
        external_ids = [path.split('/')[-1] for path in files_to_upload]

    elif csv_path is not None:
        row_dict = read_import_label_csv(csv_path)
        files_to_upload = [row['content'] for row in row_dict]

        if len(files_to_upload) == 0:
            raise ValueError(
                'No files to upload. '
                'Check your csv file')
        external_ids = [row['external_id'] for row in row_dict]

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
