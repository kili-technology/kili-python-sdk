"""Helpers to create point annotations."""

from typing import Dict, Optional, Union


def point_to_normalized_point(
    point: Dict[str, Union[int, float]],
    img_width: Optional[Union[int, float]] = None,
    img_height: Optional[Union[int, float]] = None,
) -> Dict[str, float]:
    # pylint: disable=line-too-long
    """Converts a 2D point to a Kili label format normalized point.

    The output can be used to create object detection annotations. See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation) for more details.

    A point is a dict with keys 'x' and 'y', and corresponding values in pixels (int or float).

    Conventions for the input point:

    - The origin is the bottom left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from bottom to top.

    Conventions for the output point:

    - The origin is the top left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from top to bottom.

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
        from kili.utils.labels.point import point_to_normalized_point

        normalized_point = point_to_normalized_point({"x": 5, "y": 40}, img_width=100, img_height=100)

        json_response = {
            "OBJECT_DETECTION_JOB": {
                "annotations": [
                    {
                        "point": normalized_point,
                        "categories": [{"name": "CLASS_A"}],
                        "type": "marker",
                    }
                ]
            }
        }
        ```
    """
    if (img_width is None) != (img_height is None):
        raise ValueError("img_width and img_height must be both None or both not None.")

    if img_width is not None and img_height is not None:
        point = {
            "x": point["x"] / img_width,
            "y": point["y"] / img_height,
        }

    assert 0 <= point["x"] <= 1, f"Point x coordinate {point['x']} should be in [0, 1]."
    assert 0 <= point["y"] <= 1, f"Point y coordinate {point['y']} should be in [0, 1]."

    return {"x": point["x"], "y": 1 - point["y"]}


def normalized_point_to_point(
    point: Dict[str, float],
    img_width: Optional[Union[int, float]] = None,
    img_height: Optional[Union[int, float]] = None,
) -> Dict[str, float]:
    # pylint: disable=line-too-long
    """Converts a Kili label format normalized point to a 2D point.

    It is the inverse of the method `point_to_normalized_point`.

    A point is a dict with keys 'x' and 'y', and corresponding values in pixels (int or float).

    Conventions for the input point:

    - The origin is the top left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from top to bottom.

    Conventions for the output point:

    - The origin is the bottom left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from bottom to top.

    If the image width and height are provided, the point coordinates will be scaled to the image size.
    If not, the method will keep the normalized coordinates.

    Args:
        point: Point to convert.
        img_width: Width of the image the point is defined in.
        img_height: Height of the image the point is defined in.

    Returns:
        A dict with keys 'x' and 'y', and corresponding values in pixels.
    """
    if (img_width is None) != (img_height is None):
        raise ValueError("img_width and img_height must be both None or both not None.")

    img_height = img_height or 1
    img_width = img_width or 1

    return {
        "x": point["x"] * img_width,
        "y": (1 - point["y"]) * img_height,
    }
