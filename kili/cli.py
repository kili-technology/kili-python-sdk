"""Kili CLI"""

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
@click.argument('files', type=str, nargs=-1)
@click.option('--api-key', type=str, help='Your Api Key', envvar='KILI_API_KEY')
@click.option('--project-id', type=str, help='Id of the project to import assets in')
@click.option('--exclude', '-e', type=str, multiple=True,
              help="Files to exclude from the given files")
@click.option('--frames', type=bool, help="Only for a frame project, import videos as frames")
@click.option('--fps', type=int, help="Only for a frame project, import videos with this fps")
#pylint: disable=too-many-arguments
def import_assets(api_key, project_id, files, exclude, fps, frames):
    """
    Command for adding assets into a project.

    Currently, this command does not support :
        - The import of videos from local frames, rich text and time series assets.
        - the import of assets with metadata or with a custom external_id
    For such imports, please use the `append_many_to_dataset` method in the Kili SDK.
    """
    if files is None:
        raise ValueError("No files or directory specified.")
    kili = Kili(api_key=api_key)
    input_type = kili.projects(project_id, disable_tqdm=True, fields=[
                               'inputType'])[0]['inputType']

    if input_type != 'FRAME' and (fps is not None or frames is not None):
        illegal_option = 'fps and frames are'
        if frames is None:
            illegal_option = 'fps is'
        if frames is None:
            illegal_option = 'frames is'
        raise ValueError(f'{illegal_option} only valid for a FRAME project')

    files_to_upload = get_file_to_upload(files, input_type, exclude)
    if len(files_to_upload) == 0:
        raise ValueError(
            'No files to upload.'
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
