import pytest

from kili.utils.labels import normalized_point_to_point, point_to_normalized_point


def test_point_conversion():
    point = {"x": 2.0, "y": 2.0}  # bottom left corner
    img_width = 20
    img_height = 10
    normalized_point = point_to_normalized_point(point, img_width, img_height)

    assert normalized_point == {"x": 0.1, "y": 0.8}

    assert normalized_point_to_point(normalized_point, img_width, img_height) == pytest.approx(
        point
    )
