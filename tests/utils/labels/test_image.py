import urllib.request

import cv2  # type: ignore

from kili.utils.labels import mask_to_vertices


def test_mask_to_vertices():
    mask_url = "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/master/recipes/img/HUMAN.mask.png"
    urllib.request.urlretrieve(mask_url, "mask.png")

    mask = cv2.imread("mask.png")[:, :, 0]  # keep only height and width
    mask[200:220, 200:220] = 0  # add a hole in the mask to test the hierarchy

    contours, hierarchy = mask_to_vertices(mask)

    assert len(contours) == 2
    assert hierarchy[0].tolist() == [-1, -1, 1, -1]  # first contour is the outer contour
    assert hierarchy[1].tolist() == [-1, -1, -1, 0]  # second contour is the inner contour
