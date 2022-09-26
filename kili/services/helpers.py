"""
Helpers for the services
"""
from pathlib import Path
from typing import List, Optional, TypeVar

from kili.services.exceptions import (
    NotEnoughArgumentsSpecifiedError,
    TooManyArgumentsSpecifiedError,
)

PathLike = TypeVar("PathLike", Path, str)


def check_exclusive_options(csv_path: Optional[PathLike], files: Optional[List[PathLike]]) -> None:
    """Forbid mutual use of options and argument(s)"""

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
