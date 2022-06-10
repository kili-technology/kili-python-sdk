"""Kili CLI"""

from typing import Optional, Tuple
import click
from kili.client import Kili
from kili import __version__
from kili.mutations.asset.helpers import get_file_to_upload

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    """Kili Command line interface."""


@cli.group(context_settings=CONTEXT_SETTINGS)
def project():
    """Commands to interact with a Kili project"""


@project.command(name='import')
@click.argument('files', type=click.Path(), nargs=-1)
@click.option('--api-key', type=str, envvar='KILI_API_KEY', required=True,
              help='Your Api Key')
@click.option('--project-id', type=str, required=True,
              help='Id of the project to import assets in')
@click.option('--exclude', '-e', type=click.Path(exists=True), multiple=True,
              help="Files to exclude from the given files")
@click.option('--frames', type=bool, default=False, is_flag=True,
              help="Only for a frame project, import videos as frames. "
              "The import time is longer with this option")
@click.option('--fps', type=int,
              help="Only for a frame project, import videos with this fps")
#pylint: disable=too-many-arguments
def import_assets(api_key: str,
                  project_id: str,
                  files: Tuple[str, ...],
                  exclude: Optional[Tuple[str, ...]],
                  fps: Optional[int],
                  frames: bool):
    """
    Command for adding assets into a project.

    Files can be paths to files or to folders. You can provide several paths separated by spaces.

    Currently, this command does not support:

        - the import of videos from local frames, rich text and time series assets

        - the import of assets with metadata or with a custom external_id

    For such imports, please use the `append_many_to_dataset` method in the Kili SDK.
    """
    if files is None:
        raise ValueError("No files or directory specified.")
    kili = Kili(api_key=api_key)
    input_type = kili.projects(project_id,
                               disable_tqdm=True,
                               fields=['inputType'])[0]['inputType']

    if input_type != 'FRAME' and (fps is not None or frames is True):
        illegal_option = 'fps and frames are'
        if frames is False:
            illegal_option = 'fps is'
        if fps is None:
            illegal_option = 'frames is'
        raise ValueError(f'{illegal_option} only valid for a FRAME project')

    files_to_upload = get_file_to_upload(files, input_type, exclude)
    if len(files_to_upload) == 0:
        raise ValueError(
            'No files to upload. '
            'Check that the paths exist and that the file types are compatible with the project')

    external_ids = [path.split('/')[-1] for path in files_to_upload]

    json_metadata_array = None
    if input_type == 'FRAME':
        json_metadata_array = [
            {'processingParameters': {
                'shouldKeepNativeFrameRate': fps is None,
                'framesPlayedPerSecond': fps,
                'shouldUseNativeVideo': not frames}
             }
        ] * len(files_to_upload)

    kili.append_many_to_dataset(
        project_id=project_id,
        content_array=files_to_upload,
        external_id_array=external_ids,
        json_metadata_array=json_metadata_array)


def main() -> None:
    """Execute the main function of the command line."""
    cli()


if __name__ == "__main__":
    main()
