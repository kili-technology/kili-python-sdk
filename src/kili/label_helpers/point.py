"""Helpers to create boundingPoly points annotations."""

from typing import Dict, Optional

from .types import PixelUnit


def point_to_normalized_point(
    point: Dict[str, PixelUnit],
    img_width: Optional[PixelUnit] = None,
    img_height: Optional[PixelUnit] = None,
) -> Dict[str, PixelUnit]:
    # pylint: disable=line-too-long
    """Converts a 2D point to a Kili label format normalized point.

    The output can be used to create object detection annotations. See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation) for more details.

    A point is a dict with keys 'x' and 'y', and corresponding values in pixels (int or float).

    Conventions for the input point:

    - The origin is the bottom left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from bottom to top.

    If the image width and height are provided, the point coordinates will be normalized to [0, 1].
    If not, the method expects the point coordinates to be already normalized.

    Args:
        point: Point to convert.
        img_width: Width of the image the point is defined in.
        img_height: Height of the image the point is defined in.

    Returns:
        A dict with keys 'x' and 'y', and corresponding normalized values.

    !!! Example
        ```python
        from kili.label_helpers import point_to_normalized_point

        inputs = {
            bottom_left = {"x": 0, "y": 0},
            bottom_right = {"x": 10, "y": 0},
            top_right = {"x": 10, "y": 10},
            top_left = {"x": 0, "y": 10},
            img_width = 100,
            img_height = 100,
        }
        normalized_vertices = bbox_points_to_normalized_vertices(**inputs)
        json_response = {
            "OBJECT_DETECTION_JOB": {
                "annotations": [
                    {
                        "boundingPoly": [{"normalizedVertices": normalized_vertices}],
                        "categories": [{"name": "CLASS_A"}],
                        "type": "rectangle",
                    }
                ]
            }
        }
        ```
    """
    if img_width is not None and img_height is not None:
        point = {
            "x": point["x"] / img_width,
            "y": point["y"] / img_height,
        }

    return {"x": point["x"], "y": 1 - point["y"]}
