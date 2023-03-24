"""Helpers to create boundingPoly polygon and semantic annotations."""

from typing import Dict, List, Tuple

from .types import PixelCoordType

try:
    import cv2
    import numpy as np
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
        "OpenCV and Numpy are required to use the image label creation helpers."
    ) from err


def _opencv_contour_to_normalized_vertices(
    contour: np.ndarray, img_width: PixelCoordType, img_height: PixelCoordType
) -> List[Dict[str, PixelCoordType]]:
    contour_points = []
    for point in contour:
        point = point[0]
        x = point[0]  # pylint:disable=invalid-name
        y = point[1]  # pylint:disable=invalid-name
        contour_points.append({"x": x / img_width, "y": y / img_height})
    return contour_points


def mask_to_vertices(image: np.ndarray) -> Tuple[List[List[Dict[str, PixelCoordType]]], np.ndarray]:
    # pylint: disable=line-too-long
    """Converts a binary mask to a list of normalized vertices using OpenCV [cv2.findContours](https://docs.opencv.org/4.7.0/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0).

    The output can be used to create "boundingPoly" polygon or semantic annotations.
    See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#standard-object-detection) for more details.

    Args:
        image: Binary mask. Should be an array of shape (height, width) with values 0 and 255.

    Returns:
        Tuple: A tuple containing a list of normalized vertices and the hierarchy of the contours (see [documentation](https://docs.opencv.org/4.7.0/d9/d8b/tutorial_py_contours_hierarchy.html)).

    !!! Example
        ```python
        import urllib.request
        import cv2
        from kili.utils.labels import mask_to_vertices

        img_url = "https://farm7.staticflickr.com/6153/6181981748_6a225c275d_z.jpg"
        mask_url = "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/master/recipes/img/HUMAN.mask.png"

        urllib.request.urlretrieve(img_url, "img.jpg")
        urllib.request.urlretrieve(mask_url, "mask.png")

        img = cv2.imread("mask.png")[:, :, 0]  # keep only height and width
        img[200:220, 200:220] = 0  # add a hole in the mask to test the hierarchy

        contours, hierarchy = mask_to_vertices(img)
        # hierarchy tells us that the first contour is the outer contour
        # and the second one is the inner contour

        json_response = {
            "OBJECT_DETECTION_JOB": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {"normalizedVertices": contours[0]},  # outer contour
                            {"normalizedVertices": contours[1]},  # inner contour
                        ],
                        "categories": [{"name": "A"}],
                        "type": "semantic",
                    }
                ]
            }
        }
        ```
    """
    if image.ndim > 2:
        raise ValueError(f"Image should be a 2D array, got {image.ndim}D array")

    unique_values = np.unique(image).tolist()
    if unique_values != [0, 255]:
        raise ValueError(f"Image should be binary, got {unique_values}")

    img_height, img_width = image.shape
    # pylint:disable=no-member
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = [
        _opencv_contour_to_normalized_vertices(contour, img_width, img_height)
        for contour in contours
    ]
    hierarchy = hierarchy[0]

    return contours, hierarchy
