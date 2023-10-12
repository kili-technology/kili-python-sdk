"""Helpers to create boundingPoly polygon and semantic annotations."""

from typing import Dict, List, Tuple, Union

try:
    import cv2  # type: ignore
    import numpy as np
except ModuleNotFoundError as err:
    raise ModuleNotFoundError(
        "OpenCV and Numpy are required to use the image label creation helpers. To install them,"
        " run: pip install kili[image-utils]."
    ) from err


def _opencv_contour_to_normalized_vertices(
    contour: np.ndarray, img_width: Union[int, float], img_height: Union[int, float]
) -> List[Dict[str, float]]:
    contour_points = []
    for point in contour:
        point = point[0]
        x = point[0]
        y = point[1]
        contour_points.append({"x": x / img_width, "y": y / img_height})
    return contour_points


def mask_to_normalized_vertices(
    image: np.ndarray,
) -> Tuple[List[List[Dict[str, float]]], np.ndarray]:
    # pylint: disable=line-too-long
    """Converts a binary mask to a list of normalized vertices using OpenCV [cv2.findContours](https://docs.opencv.org/4.7.0/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0).

    The output can be used to create "boundingPoly" polygon or semantic annotations.
    See the [documentation](https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#standard-object-detection) for more details.

    Args:
        image: Binary mask. Should be an array of shape (height, width) with values in {0, 255}.

    Returns:
        Tuple: A tuple containing a list of normalized vertices and the hierarchy of the contours (see [OpenCV documentation](https://docs.opencv.org/4.7.0/d9/d8b/tutorial_py_contours_hierarchy.html)).

    !!! Example
        ```python
        import urllib.request
        import cv2
        from kili.utils.labels.image import mask_to_normalized_vertices

        mask_url = "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/main/recipes/img/HUMAN.mask.png"
        urllib.request.urlretrieve(mask_url, "mask.png")

        img = cv2.imread("mask.png")[:, :, 0]  # keep only height and width
        img[200:220, 200:220] = 0  # add a hole in the mask to test the hierarchy

        contours, hierarchy = mask_to_normalized_vertices(img)
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
    if not all(value in [0, 255] for value in unique_values):
        raise ValueError(f"Image should be binary with values in {{0, 255}}, got {unique_values}")

    img_height, img_width = image.shape
    # pylint:disable=no-member
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # type: ignore

    contours = [
        _opencv_contour_to_normalized_vertices(contour, img_width, img_height)
        for contour in contours
    ]
    hierarchy = hierarchy[0]

    return contours, hierarchy


def normalized_vertices_to_mask(
    normalized_vertices: List[Dict[str, float]], img_width: int, img_height: int
) -> np.ndarray:
    # pylint: disable=line-too-long
    """Converts a Kili label with normalized vertices to a binary mask.

    It is the inverse of the method `mask_to_normalized_vertices`.

    Args:
        normalized_vertices: A list of normalized vertices.
        img_width: Width of the image the segmentation is defined in.
        img_height: Height of the image the segmentation is defined in.

    Returns:
        A numpy array of shape (height, width) with values in {0, 255}.

    !!! Example
        ```python
        from kili.utils.labels.image import normalized_vertices_to_mask

        # if using raw dict label:
        normalized_vertices = label["jsonResponse"]["OBJECT_DETECTION_JOB"]["annotations"][0]["boundingPoly"][0]["normalizedVertices"]

        # if using parsed label:
        normalized_vertices = label.jobs["OBJECT_DETECTION_JOB"].annotations[0].bounding_poly[0].normalized_vertices

        img_height, img_width = 1080, 1920
        mask = normalized_vertices_to_mask(normalized_vertices, img_width, img_height)
        plt.imshow(mask)
        plt.show()
        ```
    """
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    polygon = [
        [
            int(round(vertice["x"] * img_width)),
            int(round(vertice["y"] * img_height)),
        ]
        for vertice in normalized_vertices
    ]
    polygon = np.array([polygon])
    cv2.fillPoly(img=mask, pts=polygon, color=255)  # type: ignore  # pylint:disable=no-member
    return mask
