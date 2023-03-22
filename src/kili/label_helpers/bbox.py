"""Helpers to create boundingPoly annotations."""

from typing import Dict, List, Optional, Union

PixelUnit = Union[int, float]


def bbox_points_to_normalized_vertices(
    *,
    bottom_left: Dict[str, PixelUnit],
    bottom_right: Dict[str, PixelUnit],
    top_right: Dict[str, PixelUnit],
    top_left: Dict[str, PixelUnit],
    img_width: Optional[PixelUnit] = None,
    img_height: Optional[PixelUnit] = None,
) -> List[Dict[str, PixelUnit]]:
    # pylint: disable=line-too-long
    """Converts a bounding box defined by its 4 points to normalized vertices.

    A point is a dict with keys 'x' and 'y', and values in pixels (int or float).

    The origin is the bottom left corner of the image.
    x-axis is horizontal and goes from left to right.
    y-axis is vertical and goes from bottom to top.

    If the image width and height are provided, the point coordinates will be normalized to [0, 1].
    If not, the method expects the coordinates to be already normalized.

    Args:
        bottom_left: Bottom left point of the bounding box.
        bottom_right: Bottom right point of the bounding box.
        top_right: Top right point of the bounding box.
        top_left: Top left point of the bounding box.
        img_width: Width of the image the bounding box is defined in.
        img_height: Height of the image the bounding box is defined in.

    Returns:
        A list of normalized vertices.
            See https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#standard-object-detection for more details.
    """
    assert bottom_left["x"] <= bottom_right["x"], "bottom_left.x must be <= bottom_right.x"
    assert top_left["x"] <= top_right["x"], "top_left.x must be <= top_right.x"
    assert bottom_left["y"] <= top_left["y"], "bottom_left.y must be <= top_left.y"
    assert bottom_right["y"] <= top_right["y"], "bottom_right.y must be <= top_right.y"

    if img_width is not None and img_height is not None:
        bottom_left = {
            "x": bottom_left["x"] / img_width,
            "y": bottom_left["y"] / img_height,
        }
        bottom_right = {
            "x": bottom_right["x"] / img_width,
            "y": bottom_right["y"] / img_height,
        }
        top_right = {
            "x": top_right["x"] / img_width,
            "y": top_right["y"] / img_height,
        }
        top_left = {
            "x": top_left["x"] / img_width,
            "y": top_left["y"] / img_height,
        }

    vertices = [
        {"x": top_left["x"], "y": 1 - top_left["y"]},
        {"x": bottom_left["x"], "y": 1 - bottom_left["y"]},
        {"x": bottom_right["x"], "y": 1 - bottom_right["y"]},
        {"x": top_right["x"], "y": 1 - top_right["y"]},
    ]

    return vertices
