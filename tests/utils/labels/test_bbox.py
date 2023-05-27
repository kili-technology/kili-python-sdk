import pytest

from kili.utils.labels.bbox import (
    bbox_points_to_normalized_vertices,
    normalized_vertices_to_bbox_points,
)


@pytest.mark.parametrize(
    "test_name,inputs,output,origin_location",
    [
        (
            "box full image pixels",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1920, "y": 0},
                "top_right": {"x": 1920, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [{"x": 0, "y": 1}, {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}],
            "bottom_left",
        ),
        (
            "box full image normalized pixels",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1, "y": 0},
                "top_right": {"x": 1, "y": 1},
                "top_left": {"x": 0, "y": 1},
            },
            [{"x": 0, "y": 1}, {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}],
            "bottom_left",
        ),
        (
            "box left half part of the image",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1920 / 2, "y": 0},
                "top_right": {"x": 1920 / 2, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [{"x": 0, "y": 1}, {"x": 0, "y": 0}, {"x": 0.5, "y": 0}, {"x": 0.5, "y": 1}],
            "bottom_left",
        ),
        (
            "box left half part of the image already normalized",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 0.5, "y": 0},
                "top_right": {"x": 0.5, "y": 1},
                "top_left": {"x": 0, "y": 1},
            },
            [{"x": 0, "y": 1}, {"x": 0, "y": 0}, {"x": 0.5, "y": 0}, {"x": 0.5, "y": 1}],
            "bottom_left",
        ),
        (
            "box right half part of the image",
            {
                "bottom_left": {"x": 0.5, "y": 0},
                "bottom_right": {"x": 1, "y": 0},
                "top_right": {"x": 1, "y": 1},
                "top_left": {"x": 0.5, "y": 1},
            },
            [{"x": 0.5, "y": 1}, {"x": 0.5, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}],
            "bottom_left",
        ),
        (
            "box horizontal center part of the image full width",
            {
                "bottom_left": {"x": 0.0, "y": 0.25},
                "bottom_right": {"x": 1, "y": 0.25},
                "top_right": {"x": 1, "y": 0.75},
                "top_left": {"x": 0.0, "y": 0.75},
            },
            [{"x": 0, "y": 0.75}, {"x": 0, "y": 0.25}, {"x": 1, "y": 0.25}, {"x": 1, "y": 0.75}],
            "bottom_left",
        ),
        (
            "square small box bottom left corner",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 10, "y": 0},
                "top_right": {"x": 10, "y": 10},
                "top_left": {"x": 0, "y": 10},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0, "y": 1},
                {"x": 0, "y": 1070 / 1080},
                {"x": 10 / 1920, "y": 1070 / 1080},
                {"x": 10 / 1920, "y": 1},
            ],
            "bottom_left",
        ),
        (
            "square small box bottom right corner",
            {
                "bottom_left": {"x": 1910, "y": 0},
                "bottom_right": {"x": 1920, "y": 0},
                "top_right": {"x": 1920, "y": 10},
                "top_left": {"x": 1910, "y": 10},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 1910 / 1920, "y": 1},
                {"x": 1910 / 1920, "y": 1070 / 1080},
                {"x": 1, "y": 1070 / 1080},
                {"x": 1, "y": 1},
            ],
            "bottom_left",
        ),
        (
            "square small box top right corner",
            {
                "bottom_left": {"x": 1910, "y": 1070},
                "bottom_right": {"x": 1920, "y": 1070},
                "top_right": {"x": 1920, "y": 1080},
                "top_left": {"x": 1910, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 1910 / 1920, "y": 10 / 1080},
                {"x": 1910 / 1920, "y": 0},
                {"x": 1, "y": 0},
                {"x": 1, "y": 10 / 1080},
            ],
            "bottom_left",
        ),
        (
            "square small box top left corner",
            {
                "bottom_left": {"x": 0, "y": 1070},
                "bottom_right": {"x": 10, "y": 1070},
                "top_right": {"x": 10, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0, "y": 10 / 1080},
                {"x": 0, "y": 0},
                {"x": 10 / 1920, "y": 0},
                {"x": 10 / 1920, "y": 10 / 1080},
            ],
            "bottom_left",
        ),
        (
            "small box somewhere in the top right quarter of the image",
            {
                "bottom_left": {"x": 1000, "y": 700},
                "bottom_right": {"x": 1050, "y": 700},
                "top_right": {"x": 1050, "y": 750},
                "top_left": {"x": 1000, "y": 750},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 1000 / 1920, "y": 1 - (700 / 1080)},
                {"x": 1000 / 1920, "y": 1 - (750 / 1080)},
                {"x": 1050 / 1920, "y": 1 - (750 / 1080)},
                {"x": 1050 / 1920, "y": 1 - (700 / 1080)},
            ],
            "bottom_left",
        ),
        (
            "small box top left corner of the image. input points in kili space (top_left)",
            {
                "bottom_left": {"x": 0, "y": 10},
                "bottom_right": {"x": 10, "y": 10},
                "top_right": {"x": 10, "y": 0},
                "top_left": {"x": 0, "y": 0},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0, "y": 10 / 1080},
                {"x": 0, "y": 0},
                {"x": 10 / 1920, "y": 0},
                {"x": 10 / 1920, "y": 10 / 1080},
            ],
            "top_left",
        ),
    ],
)
def test_bbox_points_to_normalized_vertices(test_name, inputs, output, origin_location):
    vertices = bbox_points_to_normalized_vertices(**inputs, origin_location=origin_location)
    for computed_vertex, expected_vertex in zip(vertices, output):  # type: ignore
        assert computed_vertex == pytest.approx(expected_vertex)

    bbox_points = normalized_vertices_to_bbox_points(
        vertices,
        img_width=inputs.get("img_width"),
        img_height=inputs.get("img_height"),
        origin_location=origin_location,
    )
    assert bbox_points["bottom_left"] == pytest.approx(inputs["bottom_left"])
    assert bbox_points["bottom_right"] == pytest.approx(inputs["bottom_right"])
    assert bbox_points["top_right"] == pytest.approx(inputs["top_right"])
    assert bbox_points["top_left"] == pytest.approx(inputs["top_left"])
