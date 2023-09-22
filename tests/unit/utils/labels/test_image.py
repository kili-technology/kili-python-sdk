import urllib.request
from copy import deepcopy
from functools import reduce
from tempfile import NamedTemporaryFile
from typing import Any, Generator

import cv2
import numpy as np
import pytest

from kili.utils.labels.image import (
    mask_to_normalized_vertices,
    normalized_vertices_to_mask,
)


@pytest.fixture()
def test_img_path() -> Generator[str, Any, None]:
    mask_url = "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/main/recipes/img/HUMAN.mask.png"
    with NamedTemporaryFile(suffix=".png") as f:
        urllib.request.urlretrieve(mask_url, f.name)
        yield f.name


def test_mask_to_normalized_vertices(test_img_path: str):
    mask = cv2.imread(test_img_path)[:, :, 0]  # pylint:disable=no-member  # type: ignore
    mask_with_hole = mask.copy()  # pylint:disable=no-member  # type: ignore
    mask_with_hole[200:220, 200:220] = 0  # add a hole in the mask to test the hierarchy

    contours, hierarchy = mask_to_normalized_vertices(mask_with_hole)
    assert len(contours) == 2
    assert hierarchy[0].tolist() == [-1, -1, 1, -1]  # first contour is the outer contour
    assert hierarchy[1].tolist() == [-1, -1, -1, 0]  # second contour is the inner contour

    # reconstruct original mask
    human_contour = contours[0]
    estimated_mask = normalized_vertices_to_mask(human_contour, mask.shape[1], mask.shape[0])
    assert (mask == estimated_mask).all()


test_img = np.zeros((20, 25), dtype=np.uint8)
# add 5 rectangles
test_img[15:20, 18:25] = 255
test_img[0:3, 0:3] = 255
test_img[16:19, 5:10] = 255
test_img[10:12, 10:12] = 255
test_img[0:5, 10:12] = 255
expected_vertices = [
    [
        {"x": 0.2, "y": 0.8},
        {"x": 0.2, "y": 0.95},
        {"x": 0.4, "y": 0.95},
        {"x": 0.4, "y": 0.8},
    ],
    [
        {"x": 0.72, "y": 0.75},
        {"x": 0.72, "y": 1},
        {"x": 1, "y": 1},
        {"x": 1, "y": 0.75},
    ],
    [
        {"x": 0.4, "y": 0.5},
        {"x": 0.4, "y": 0.6},
        {"x": 0.48, "y": 0.6},
        {"x": 0.48, "y": 0.5},
    ],
    [
        {"x": 0.4, "y": 0},
        {"x": 0.4, "y": 0.25},
        {"x": 0.48, "y": 0.25},
        {"x": 0.48, "y": 0},
    ],
    [
        {"x": 0, "y": 0},
        {"x": 0, "y": 0.15},
        {"x": 0.12, "y": 0.15},
        {"x": 0.12, "y": 0},
    ],
]


def test_given_binary_mask_when_computing_vertices_it_generates_correct_segmentation_labels():
    # Given
    img = test_img

    # When
    vertices, _ = mask_to_normalized_vertices(img)

    # Then
    assert vertices == expected_vertices


def test_given_normalized_vertices_when_converting_to_mask_then_it_works():
    # Given
    vertices = deepcopy(expected_vertices)

    # When
    masks = [normalized_vertices_to_mask(v, img_height=20, img_width=25) for v in vertices]
    mask = reduce(lambda mask_1, mask_2: np.where(mask_1 != 0, mask_1, mask_2), masks)

    # Then
    assert (mask == test_img).all()
