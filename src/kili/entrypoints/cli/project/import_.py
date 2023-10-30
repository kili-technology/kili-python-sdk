"""CLI's project import subcommand."""

import os
from typing import Iterable, Optional

import click
from typeguard import typechecked

from kili.adapters.http_client import HttpClient
from kili.core.helpers import get_file_paths_to_upload
from kili.domain.project import ProjectId
from kili.entrypoints.cli.common_args import Arguments, Options, from_csv
from kili.entrypoints.cli.helpers import collect_from_csv, get_kili_client
from kili.services import asset_import
from kili.services.helpers import (
    check_exclusive_options,
    get_external_id_from_file_path,
)


def check_asset_type(key: str, value: str, http_client: Optional[HttpClient]) -> str:
    """Type check value based on key."""
    assert (
        http_client is not None
    )  # the optional type is there only to match the collect_from_csv type check function, that may
    # not require http requests.
    if key == "content" and not os.path.isfile(value):
        resp = http_client.get(value)
        if resp.status_code != 200:
            return f"{value} is not a valid url or path to a file."

    return ""


def generate_json_metadata(as_frames: bool, fps: Optional[int]):
    # pylint: disable=line-too-long
    """Generate the json_metadata for input of the import_assets service when uploading from a list of path.

    Args:
        as_frames: for a frame project, if videos should be split in frames
        fps: for a frame project, import videos with this frame rate
    """
    return {
        "processingParameters": {
            "shouldKeepNativeFrameRate": fps is None,
            "framesPlayedPerSecond": fps,
            "shouldUseNativeVideo": not as_frames,
        }
    }


@click.command(name="import")
@Arguments.files
@Options.api_key
@Options.endpoint
@Options.project_id
@from_csv(["external_id", "content"], [])
@click.option(
    "--frames",
    "as_frames",
    type=bool,
    default=False,
    is_flag=True,
    help=(
        "Only for a frame project, import videos as frames. "
        "The import time is longer with this option."
    ),
)
@click.option(
    "--fps", type=int, help="Only for a frame project, import videos with a specific frame rate"
)
@Options.verbose
@typechecked
# pylint: disable=too-many-arguments,too-many-locals
def import_assets(
    api_key: Optional[str],
    endpoint: Optional[str],
    project_id: str,
    files: Optional[Iterable[str]],
    csv_path: Optional[str],
    fps: Optional[int],
    as_frames: bool,
    verbose: bool,  # pylint: disable=unused-argument
):
    r"""Add assets into a project.

    Files can be paths to files or to folders. You can provide several paths separated by spaces.

    If no Files are provided, --from-csv can be used to import
    assets from a CSV file with two columns:

    - `external_id`: external id of the asset.
    - `content`: paths to the asset file or a url hosting the asset.

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
        ```
        kili project import \\
            --from-csv assets_list.csv \\
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
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    input_type = kili.kili_api_gateway.get_project(ProjectId(project_id), ("inputType",))[
        "inputType"
    ]
    if input_type not in ("VIDEO_LEGACY", "VIDEO") and (fps is not None or as_frames is True):
        illegal_option = "fps and frames are"
        if not as_frames:
            illegal_option = "fps is"
        if fps is None:
            illegal_option = "frames is"
        raise ValueError(f"{illegal_option} only valid for a VIDEO project")

    check_exclusive_options(csv_path, files)

    if files:
        files_to_upload = get_file_paths_to_upload(
            list(files), file_check_function=None, verbose=False
        )
        if len(files_to_upload) == 0:
            raise ValueError(
                "No files to upload. "
                "Check that the paths exist and file types are compatible with the project"
            )
        external_ids = [get_external_id_from_file_path(path) for path in files_to_upload]

    elif csv_path is not None:
        row_dict = collect_from_csv(
            csv_path=csv_path,
            required_columns=["external_id", "content"],
            optional_columns=[],
            type_check_function=check_asset_type,
            http_client=kili.http_client,
        )

        files_to_upload = [row["content"] for row in row_dict]
        external_ids = [row["external_id"] for row in row_dict]

        if len(files_to_upload) == 0:
            raise ValueError(f"No valid asset files or url were found in csv: {csv_path}")
    else:
        raise ValueError("You must provide either the file argument of the csv_path.")

    assets_to_import = [
        {
            "content": files_to_upload[i],
            "external_id": external_ids[i],
        }
        for i in range(len(files_to_upload))
    ]
    if input_type in ("VIDEO_LEGACY", "VIDEO"):
        json_metadata = generate_json_metadata(as_frames, fps)
        assets_to_import = [
            {**assets_to_import[i], "json_metadata": json_metadata}
            for i in range(len(assets_to_import))
        ]

    asset_import.import_assets(kili, ProjectId(project_id), assets_to_import, False)
