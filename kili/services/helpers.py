"""
Helpers for the services
"""
from pathlib import Path
from typing import List, Optional, TypeVar

from kili.services.exceptions import (
    NotEnoughArgumentsSpecified,
    TooManyArgumentsSpecified,
)

PathLike = TypeVar("PathLike", Path, str)


def check_exclusive_options(csv_path: Optional[PathLike], files: Optional[List[PathLike]]) -> None:
    """Forbid mutual use of options and argument(s)"""

    if (csv_path is not None) + (files is not None and len(files) > 0) > 1:
        raise TooManyArgumentsSpecified("files arguments and option --from-csv are exclusive.")

    if (csv_path is not None) + (files is not None and len(files) > 0) == 0:
        raise NotEnoughArgumentsSpecified(
            "You must either provide file arguments or use the option --from-csv"
        )


def get_external_id_from_file_path(path: PathLike) -> str:
    """Return external_id from file's path
    ex: 'tree/leaf/file_name.txt- -> file_name
    """
    file_path = Path(path).parts[-1]
    return ".".join(file_path.split(".")[:-1])
