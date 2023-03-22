"""Helpers to create boundingPoly polygon and semantic annotations."""

from typing import Dict, List

from .types import PixelCoordType

try:
    import cv2
    import numpy as np
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
        "OpenCV and Numpy are required to use the image label creation helpers."
    ) from err


# pylint: disable=no-member
def _get_contour_points_opencv(binary_image: np.ndarray) -> List[Dict[str, PixelCoordType]]:
    img_height, img_width = binary_image.shape

    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # hierarchy: [Next, Previous, First_Child, Parent]
    contour_points = []
    for contour in contours:
        for point in contour:
            point = point[0]
            x = point[0]  # pylint:disable=invalid-name
            y = point[1]  # pylint:disable=invalid-name
            contour_points.append({"x": x / img_width, "y": y / img_height})

    return contour_points


def mask_to_vertices(image: np.ndarray) -> List[Dict[str, PixelCoordType]]:
    # pylint: disable=line-too-long
    """Converts a binary mask to a list of normalized vertices.

    The output can be used to create a boundingPoly polygon annotation. See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#standard-object-detection) for more details.

    Args:
        image: Binary mask. Should be an array of shape (height, width) with values 0 and 255.

    Returns:
        A list of normalized vertices.
    """
    if image.ndim > 2:
        raise ValueError(f"Image should be a 2D array, got {image.ndim}D array")

    unique_values = np.unique(image).tolist()
    if unique_values != [0, 255]:
        raise ValueError(f"Image should be binary, got {unique_values}")

    contour_points = _get_contour_points_opencv(image)

    return contour_points
