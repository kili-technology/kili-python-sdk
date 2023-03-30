import os
import urllib.request

import cv2  # type: ignore
import numpy as np

from kili.utils.labels import mask_to_normalized_vertices, normalized_vertices_to_mask


def test_mask_to_normalized_vertices():
    mask_url = "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/master/recipes/img/HUMAN.mask.png"
    urllib.request.urlretrieve(mask_url, "mask.png")

    mask = cv2.imread("mask.png")[:, :, 0]  # pylint:disable=no-member
    mask[200:220, 200:220] = 0  # add a hole in the mask to test the hierarchy

    contours, hierarchy = mask_to_normalized_vertices(mask)

    assert len(contours) == 2
    assert hierarchy[0].tolist() == [-1, -1, 1, -1]  # first contour is the outer contour
    assert hierarchy[1].tolist() == [-1, -1, -1, 0]  # second contour is the inner contour

    human_contour = contours[0]
    estimated_mask = normalized_vertices_to_mask(human_contour, mask.shape[1], mask.shape[0])

    assert estimated_mask.shape == mask.shape
    same_pixels = np.sum(estimated_mask == mask)
    total_pixels = mask.shape[0] * mask.shape[1]
    assert same_pixels / total_pixels >= 0.99

    os.remove("mask.png")
