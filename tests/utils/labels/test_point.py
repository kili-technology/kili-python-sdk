from kili.utils.labels import point_to_normalized_point


def test_point_to_normalized_point():
    point = {"x": 1, "y": 2}  # bottom left corner
    img_width = 10
    img_height = 10
    normalized_point = point_to_normalized_point(point, img_width, img_height)

    assert normalized_point == {"x": 0.1, "y": 0.8}
