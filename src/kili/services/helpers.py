"""
Helpers for the services
"""
from pathlib import Path
from typing import Iterable, Optional, TypeVar

from kili.services.exceptions import (
    NotEnoughArgumentsSpecifiedError,
    TooManyArgumentsSpecifiedError,
)

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
    json_interface = list(kili.projects(project_id=project_id, fields=["jsonInterface"]))[0][
        "jsonInterface"
    ]
    return target_job_name in json_interface["jobs"]
