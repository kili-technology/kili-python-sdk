"""
Helpers for the services
"""
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, TypeVar

from typeguard import typechecked

from kili.exceptions import NotFound
from kili.services.exceptions import (
    NotEnoughArgumentsSpecifiedError,
    TooManyArgumentsSpecifiedError,
)
from kili.services.project import get_project_field

PathLike = TypeVar("PathLike", Path, str)


def check_exclusive_options(
    csv_path: Optional[PathLike], files: Optional[Iterable[PathLike]]
) -> None:
    """Forbid mutual use of options and argument(s)"""
    if files is not None:
        files = list(files)

    if (csv_path is not None) + (files is not None and len(files) > 0) > 1:
        raise TooManyArgumentsSpecifiedError(
            "An explicit list of files and a CSV file containing label files"
            " can't be specified at the same time"
        )

    if (csv_path is not None) + (files is not None and len(files) > 0) == 0:
        raise NotEnoughArgumentsSpecifiedError(
            "You must either provide an explicit list of files or a CSV file containing a file list"
        )


def get_external_id_from_file_path(path: PathLike) -> str:
    """Return external_id from file's path
    ex: 'tree/leaf/file_name.txt- -> file_name
    """
    file_path = Path(path).parts[-1]
    return ".".join(file_path.split(".")[:-1])


def is_target_job_in_json_interface(kili, project_id: str, target_job_name: str):
    """Tell if the target job id is defined in the project's JSON interface"""
    json_interface = get_project_field(kili, project_id, "jsonInterface")
    return target_job_name in json_interface["jobs"]


@typechecked
def infer_ids_from_external_ids(
    kili, asset_external_ids: List[str], project_id: str
) -> Dict[str, str]:
    """
    Infer asset ids from their external ids and project Id.

    Returns a dict that maps external ids to internal ids.

    Args:
        asset_id: asset id
        external_id: external id
        project_id: project id
    """
    assets = kili.assets(
        external_id_contains=asset_external_ids,
        project_id=project_id,
        fields=["id", "externalId"],
        disable_tqdm=True,
    )
    id_map: Dict[str, str] = {}
    for asset in assets:
        id_map[asset["externalId"]] = asset["id"]

    if len(id_map) < len(set(asset_external_ids)):
        assets_not_found = [
            external_id for external_id in asset_external_ids if external_id not in id_map
        ]
        raise NotFound(
            f"The assets whose external_id are: {assets_not_found} have not been found in the"
            f" project of Id {project_id}"
        )
    if len(id_map) > len(set(asset_external_ids)):
        raise NotFound(
            "Several assets have been found for the same external_id. Please consider using asset"
            " ids instead."
        )
    return id_map


def assert_all_arrays_have_same_size(arrays: List[Optional[List[Any]]], raise_error=True):
    """Assert that all given arrays have the same size if they are not None"""
    sizes_arrays = {len(array) for array in arrays if array is not None}
    if len(sizes_arrays) > 1:
        if raise_error:
            raise ValueError("All arrays should have the same length")
        return False
    return True
