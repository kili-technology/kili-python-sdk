import pytest

from kili.utils.labels.point import normalized_point_to_point, point_to_normalized_point


def test_point_conversion_origin_bottom_left():
    # point bottom left side of the image
    point = {"x": 2.0, "y": 2.0}
    img_width = 20
    img_height = 10

    normalized_point = point_to_normalized_point(
        point, img_width, img_height, origin_location="bottom_left"
    )

    assert normalized_point == {"x": 0.1, "y": 0.8}

    assert normalized_point_to_point(
        normalized_point,
        img_width,
        img_height,
        origin_location="bottom_left",  # type: ignore
    ) == pytest.approx(point)


def test_point_conversion_origin_top_left():
    # point top right side of the image
    point = {"x": 19.0, "y": 1.0}
    img_width = 20
    img_height = 10

    normalized_point = point_to_normalized_point(
        point, img_width, img_height, origin_location="top_left"
    )

    assert normalized_point == {"x": 19 / 20, "y": 1 / 10}

    assert normalized_point_to_point(
        normalized_point,
        img_width,
        img_height,
        origin_location="top_left",  # type: ignore
    ) == pytest.approx(point)


def test_origin_location_point_to_normalized_point():
    point = {"x": 0.4, "y": 0.1}
    assert point_to_normalized_point(point, origin_location="top_left") == {"x": 0.4, "y": 0.1}
    assert point_to_normalized_point(point, origin_location="bottom_left") == {"x": 0.4, "y": 0.9}


def test_origin_location_normalized_point_to_point():
    # vertex middle of the image (kili space)
    vertex = {"x": 0.5, "y": 0.5}
    assert (
        normalized_point_to_point(vertex, origin_location="top_left")
        == normalized_point_to_point(vertex, origin_location="bottom_left")
        == vertex
    )

    # vertex top left corner of the image (kili space)
    vertex = {"x": 0.4, "y": 0.1}
    assert normalized_point_to_point(vertex, origin_location="top_left") == {"x": 0.4, "y": 0.1}

    # vertex top left corner of the image (kili space)
    vertex = {"x": 0.4, "y": 0.1}
    assert normalized_point_to_point(vertex, origin_location="bottom_left") == {"x": 0.4, "y": 0.9}
