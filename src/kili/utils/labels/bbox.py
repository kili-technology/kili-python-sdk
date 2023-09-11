"""Helpers to create boundingPoly rectangle annotations."""

from typing import Dict, List, Literal, Optional, Union

from .point import normalized_point_to_point, point_to_normalized_point


def bbox_points_to_normalized_vertices(
    *,
    bottom_left: Dict[str, Union[int, float]],
    bottom_right: Dict[str, Union[int, float]],
    top_right: Dict[str, Union[int, float]],
    top_left: Dict[str, Union[int, float]],
    img_width: Optional[Union[int, float]] = None,
    img_height: Optional[Union[int, float]] = None,
    origin_location: Literal["top_left", "bottom_left"] = "bottom_left",
) -> List[Dict[Literal["x", "y"], float]]:
    # pylint: disable=line-too-long
    """Converts a bounding box defined by its 4 points to normalized vertices.

    The output can be used to create a boundingPoly rectangle annotation. See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#standard-object-detection) for more details.

    A point is a dict with keys `"x"` and `"y"`, and corresponding values in pixels (`int` or `float`).

    Conventions for the input points:

    - The origin is defined by the `origin_location` argument.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical. If `origin_location` is `"top_left"`, it goes from top to bottom. If `origin_location` is `"bottom_left"`, it goes from bottom to top.

    Conventions for the output vertices:

    - The origin is the top left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from top to bottom.

    If the image width and height are provided, the input point coordinates will be normalized to `[0, 1]`.
    If not, the method expects the input points' coordinates to be already normalized.

    Args:
        bottom_left: Bottom left point of the bounding box.
        bottom_right: Bottom right point of the bounding box.
        top_right: Top right point of the bounding box.
        top_left: Top left point of the bounding box.
        img_width: Width of the image the bounding box is defined in.
        img_height: Height of the image the bounding box is defined in.
        origin_location: Location of the origin of input point coordinate system. Can be either `top_left` or `bottom_left`.

    Returns:
        A list of normalized vertices.

    !!! Example
        ```python
        from kili.utils.labels.bbox import bbox_points_to_normalized_vertices

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
    assert bottom_left["x"] <= bottom_right["x"], "bottom_left.x must be <= bottom_right.x"
    assert top_left["x"] <= top_right["x"], "top_left.x must be <= top_right.x"
    if origin_location == "bottom_left":
        assert bottom_left["y"] <= top_left["y"], "bottom_left.y must be <= top_left.y"
        assert bottom_right["y"] <= top_right["y"], "bottom_right.y must be <= top_right.y"
    elif origin_location == "top_left":
        assert bottom_left["y"] >= top_left["y"], "bottom_left.y must be >= top_left.y"
        assert bottom_right["y"] >= top_right["y"], "bottom_right.y must be >= top_right.y"

    if (img_width is None) != (img_height is None):
        raise ValueError("img_width and img_height must be both None or both not None.")

    return [
        point_to_normalized_point(
            point, img_width=img_width, img_height=img_height, origin_location=origin_location
        )
        for point in (bottom_left, top_left, top_right, bottom_right)
    ]


def normalized_vertices_to_bbox_points(
    normalized_vertices: List[Dict[str, float]],
    img_width: Optional[Union[int, float]] = None,
    img_height: Optional[Union[int, float]] = None,
    origin_location: Literal["top_left", "bottom_left"] = "bottom_left",
) -> Dict[
    Literal["top_left", "bottom_left", "bottom_right", "top_right"], Dict[Literal["x", "y"], float]
]:
    # pylint: disable=line-too-long
    """Converts a rectangle normalizedVertices annotation to a bounding box defined by 4 points.

    It is the inverse of the method `bbox_points_to_normalized_vertices`.

    A point is a dict with keys `"x"` and `"y"`, and corresponding values in pixels (`int` or `float`).

    Conventions for the input vertices:

    - The origin is the top left corner of the image.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical and goes from top to bottom.

    Conventions for the output points (`top_left`, `bottom_left`, `bottom_right`, `top_right`):

    - The origin is defined by the `origin_location` argument.
    - x-axis is horizontal and goes from left to right.
    - y-axis is vertical. If `origin_location` is `"top_left"`, it goes from top to bottom. If `origin_location` is `"bottom_left"`, it goes from bottom to top.

    If the image width and height are provided, the output point coordinates will be scaled to the image size.
    If not, the method will return the output points' coordinates normalized to `[0, 1]`.

    Args:
        normalized_vertices: A list of normalized vertices.
        img_width: Width of the image the bounding box is defined in.
        img_height: Height of the image the bounding box is defined in.
        origin_location: Location of the origin of output point coordinate system. Can be either `top_left` or `bottom_left`.

    Returns:
        A dict with keys `"top_left"`, `"bottom_left"`, `"bottom_right"`, `"top_right"`, and corresponding points.

    !!! Example
        ```python
        from kili.utils.labels.bbox import normalized_vertices_to_bbox_points

        # if using raw dict label:
        normalized_vertices = label["jsonResponse"]["OBJECT_DETECTION_JOB"]["annotations"][0]["boundingPoly"][0]["normalizedVertices"]

        # if using parsed label:
        normalized_vertices = label.jobs["OBJECT_DETECTION_JOB"].annotations[0].bounding_poly[0].normalized_vertices

        img_height, img_width = 1080, 1920
        bbox_points = normalized_vertices_to_bbox_points(normalized_vertices, img_width, img_height)
        ```
    """
    if len(normalized_vertices) != 4:
        raise ValueError(f"normalized_vertices must have length 4. Got {len(normalized_vertices)}.")

    if (img_width is None) != (img_height is None):
        raise ValueError("img_width and img_height must be both None or both not None.")

    img_height = img_height or 1
    img_width = img_width or 1

    ret = {}

    for vertex, point_name in zip(
        normalized_vertices, ("bottom_left", "top_left", "top_right", "bottom_right")
    ):
        ret[point_name] = normalized_point_to_point(
            vertex, img_width=img_width, img_height=img_height, origin_location=origin_location
        )

    return ret
