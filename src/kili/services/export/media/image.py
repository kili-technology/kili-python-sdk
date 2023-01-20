"""Tools for export with images."""

from pathlib import Path
from typing import Tuple, Union

from PIL import Image


def get_image_dimensions(file_path: Union[Path, str]) -> Tuple:
    """
    Get an image width and height
    """
    assert Path(file_path).is_file(), f"File {file_path} does not exist"
    image = Image.open(str(file_path))
    return image.size
