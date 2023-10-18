"""Tempfile utils."""

import tempfile
from pathlib import Path


class TemporaryDirectory:
    """Wrapper over temporary directory to output paths."""

    def __init__(self) -> None:
        self.temporary_directory = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )

    def __enter__(self) -> Path:
        return Path(self.temporary_directory.__enter__())

    def __exit__(self, type_, value, traceback) -> None:
        self.temporary_directory.__exit__(type_, value, traceback)
