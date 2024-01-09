from typing import Dict, List

import pytest

from kili.adapters.kili_api_gateway.label.annotation_to_json_response import (
    _classic_annotations_to_json_response,
    _interpolate_point,
    _interpolate_rectangle,
    _video_annotations_to_json_response,
)
from kili.domain.annotation import ClassicAnnotation, Vertice, VideoAnnotation

from .test_data import (
    test_case_1,
    test_case_2,
    test_case_3,
    test_case_4,
    test_case_5,
    test_case_6,
    test_case_7,
    test_case_8,
    test_case_9,
    test_case_10,
    test_case_11,
    test_case_12,
    test_case_14,
)


@pytest.mark.parametrize(
    ("test_case_name", "annotations", "expected_json_resp", "json_interface"),
    [
        (
            "test_case_1",
            test_case_1.annotations,
            test_case_1.expected_json_resp,
            test_case_1.json_interface,
        ),
        (
            "test_case_2",
            test_case_2.annotations,
            test_case_2.expected_json_resp,
            test_case_2.json_interface,
        ),
        (
            "test_case_3",
            test_case_3.annotations,
            test_case_3.expected_json_resp,
            test_case_3.json_interface,
        ),
        (
            "test_case_4",
            test_case_4.annotations,
            test_case_4.expected_json_resp,
            test_case_4.json_interface,
        ),
        (
            "test_case_5",
            test_case_5.annotations,
            test_case_5.expected_json_resp,
            test_case_5.json_interface,
        ),
        (
            "test_case_6",
            test_case_6.annotations,
            test_case_6.expected_json_resp,
            test_case_6.json_interface,
        ),
        (
            "test_case_7",
            test_case_7.annotations,
            test_case_7.expected_json_resp,
            test_case_7.json_interface,
        ),
        (
            "test_case_8",
            test_case_8.annotations,
            test_case_8.expected_json_resp,
            test_case_8.json_interface,
        ),
        (
            "test_case_9",
            test_case_9.annotations,
            test_case_9.expected_json_resp,
            test_case_9.json_interface,
        ),
        (
            "test_case_10",
            test_case_10.annotations,
            test_case_10.expected_json_resp,
            test_case_10.json_interface,
        ),
        (
            "test_case_11",
            test_case_11.annotations,
            test_case_11.expected_json_resp,
            test_case_11.json_interface,
        ),
        (
            "test_case_12",
            test_case_12.annotations,
            test_case_12.expected_json_resp,
            test_case_12.json_interface,
        ),
    ],
)
def test_given_video_label_annotations_when_converting_to_json_resp_it_works(
    test_case_name: str,
    annotations: List[VideoAnnotation],
    expected_json_resp: Dict,
    json_interface: Dict,
):
    # Given
    _ = annotations

    # When
    json_resp = _video_annotations_to_json_response(annotations, json_interface=json_interface)

    # Then
    assert json_resp == expected_json_resp


@pytest.mark.parametrize(
    ("test_case_name", "annotations", "expected_json_resp"),
    [
        (
            "test_case_14",
            test_case_14.annotations,
            test_case_14.expected_json_resp,
        ),
    ],
)
def test_given_classic_label_annotations_when_converting_to_json_resp_it_works(
    test_case_name: str,
    annotations: List[ClassicAnnotation],
    expected_json_resp: Dict,
):
    # Given
    _ = annotations

    # When
    json_resp = _classic_annotations_to_json_response(annotations)

    # Then
    assert json_resp == expected_json_resp


@pytest.mark.parametrize(
    ("previous_point", "next_point", "weight", "expected_point"),
    [
        (Vertice(x=0, y=0), Vertice(x=1, y=1), 0, Vertice(x=0, y=0)),
        (Vertice(x=0, y=0), Vertice(x=1, y=1), 1, Vertice(x=1, y=1)),
        (Vertice(x=0, y=0), Vertice(x=1, y=1), 0.5, Vertice(x=0.5, y=0.5)),
        (Vertice(x=0, y=0), Vertice(x=1, y=0), 0.3, Vertice(x=0.3, y=0)),
        (Vertice(x=0, y=0), Vertice(x=0, y=1), 0.7, Vertice(x=0.0, y=0.7)),
        (Vertice(x=0, y=1), Vertice(x=0, y=0.5), 0.5, Vertice(x=0.0, y=0.75)),
    ],
)
def test_given_two_keypoint_annotations_when_interpolate_then_it_works(
    previous_point, next_point, weight, expected_point
):
    # Given

    # When
    interpolated_point = _interpolate_point(
        previous_point=previous_point, next_point=next_point, weight=weight
    )

    # Then
    assert interpolated_point == expected_point


@pytest.mark.parametrize(
    (
        "bbox_start",
        "bbox_end",
        "weight",
        "expected_bbox",
    ),
    [
        (
            [
                {"x": 0.012, "y": 0.077},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.077},
            ],
            [
                {"x": 0.012, "y": 0.088},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.088},
            ],
            0,
            [
                {"x": 0.223, "y": 0.077},
                {"x": 0.223, "y": 0.030},
                {"x": 0.012, "y": 0.030},
                {"x": 0.012, "y": 0.077},
            ],
        ),
        (
            [
                {"x": 0.012, "y": 0.077},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.077},
            ],
            [
                {"x": 0.012, "y": 0.088},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.088},
            ],
            1,
            [
                {"x": 0.223, "y": 0.088},
                {"x": 0.223, "y": 0.030},
                {"x": 0.012, "y": 0.030},
                {"x": 0.012, "y": 0.088},
            ],
        ),
        (
            [
                {"x": 0.012, "y": 0.077},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.077},
            ],
            [
                {"x": 0.012 + 0.5, "y": 0.077},
                {"x": 0.012 + 0.5, "y": 0.030},
                {"x": 0.223 + 0.5, "y": 0.030},
                {"x": 0.223 + 0.5, "y": 0.077},
            ],
            0.5,
            [
                {"x": 0.223 + 0.25, "y": 0.077},
                {"x": 0.223 + 0.25, "y": 0.030},
                {"x": 0.012 + 0.25, "y": 0.030},
                {"x": 0.012 + 0.25, "y": 0.077},
            ],
        ),
        (
            [
                {"x": 0.012, "y": 0.077},
                {"x": 0.012, "y": 0.030},
                {"x": 0.223, "y": 0.030},
                {"x": 0.223, "y": 0.077},
            ],
            [
                {"x": 0.012 + 0.3, "y": 0.077},
                {"x": 0.012 + 0.3, "y": 0.030},
                {"x": 0.223 + 0.3, "y": 0.030},
                {"x": 0.223 + 0.3, "y": 0.077},
            ],
            1 / 3,
            [
                {"x": 0.223 + 0.1, "y": 0.077},
                {"x": 0.223 + 0.1, "y": 0.030},
                {"x": 0.012 + 0.1, "y": 0.030},
                {"x": 0.012 + 0.1, "y": 0.077},
            ],
        ),
    ],
)
def test_given_two_bboxes_on_different_frames_when_generating_intermediate_bboxes_it_works(
    bbox_start: List[Vertice],
    bbox_end: List[Vertice],
    weight: float,
    expected_bbox: List[Vertice],
):
    # Given

    # When
    interpolated_bbox = _interpolate_rectangle(
        previous_vertices=bbox_start, next_vertices=bbox_end, weight=weight
    )

    # Then
    for vertice_interpolated, vertice_expected in zip(interpolated_bbox, expected_bbox):
        assert vertice_interpolated["x"] == pytest.approx(vertice_expected["x"], 1e-3)
        assert vertice_interpolated["y"] == pytest.approx(vertice_expected["y"], 1e-3)
