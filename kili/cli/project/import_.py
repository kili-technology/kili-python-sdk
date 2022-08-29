"""CLI's project import subcommand"""

import os
import urllib.request
from typing import Dict, List, Optional, Tuple, cast

import click
from typeguard import typechecked

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.helpers import (
    check_exclusive_options,
    collect_from_csv,
    get_external_id_from_file_path,
    get_kili_client,
)
from kili.exceptions import NotFound
from kili.helpers import file_check_function_from_input_type, get_file_paths_to_upload
from kili.mutations.asset.helpers import generate_json_metadata_array

# pylint: disable=consider-using-with


def type_check_asset(key, value):
    """type check value based on key"""
    if (
        key == "content"
        and not os.path.isfile(value)
        and not urllib.request.urlopen(value).getcode() == 200
    ):
        return f"{value} is not a valid url or path to a file."

    return ""


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
    help="Only for a frame project, import videos as frames. "
    "The import time is longer with this option.",
)
@click.option(
    "--fps", type=int, help="Only for a frame project, import videos with a specific frame rate"
)
@Options.verbose
@typechecked
# pylint: disable=too-many-arguments
def import_assets(
    api_key: Optional[str],
    endpoint: Optional[str],
    project_id: str,
    files: Optional[Tuple[str, ...]],
    csv_path: Optional[str],
    fps: Optional[int],
    as_frames: bool,
    verbose: bool,
):
    """
    Add assets into a project

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
    try:
        input_type = cast(
            List[Dict], kili.projects(project_id, disable_tqdm=True, fields=["inputType"])
        )[0]["inputType"]
    except:
        # pylint: disable=raise-missing-from
        raise NotFound(f"project ID: {project_id}")

    if input_type not in ("FRAME", "VIDEO") and (fps is not None or as_frames is True):
        illegal_option = "fps and frames are"
        if not as_frames:
            illegal_option = "fps is"
        if fps is None:
            illegal_option = "frames is"
        raise ValueError(f"{illegal_option} only valid for a VIDEO project")

    check_exclusive_options(csv_path, files)

    if len(files) > 0:
        files_to_upload = get_file_paths_to_upload(
            files, file_check_function_from_input_type(input_type), verbose
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
            type_check_function=type_check_asset,
        )

        files_to_upload = [row["content"] for row in row_dict]
        external_ids = [row["external_id"] for row in row_dict]

        if len(files_to_upload) == 0:
            raise ValueError(f"No valid asset files or url were found in csv: {csv_path}")

    json_metadata_array = generate_json_metadata_array(
        as_frames, fps, len(files_to_upload), input_type
    )

    kili.append_many_to_dataset(
        project_id=project_id,
        content_array=files_to_upload,
        external_id_array=external_ids,
        json_metadata_array=json_metadata_array,
    )

    if as_frames:
        print(
            f"The import of {len(files_to_upload)} files have just started, "
            "you will receive a notification as soon as it is ready."
        )
    else:
        print(f"{len(files_to_upload)} files have been successfully imported")
