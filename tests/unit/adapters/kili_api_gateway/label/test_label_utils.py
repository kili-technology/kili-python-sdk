from typing import Dict, List

import pytest
from kili_formats.tool.annotations_to_json_response import (
    _classic_annotations_to_json_response,
    _interpolate_point,
    _interpolate_rectangle,
    _video_annotations_to_json_response,
)
from kili_formats.types import ClassicAnnotation, VideoAnnotation

from kili.domain.annotation import Vertice

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
    test_case_15,
    test_case_16,
    test_case_17,
    test_case_18,
    test_case_19,
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
        (
            "test_case_15",
            test_case_15.annotations,
            test_case_15.expected_json_resp,
            test_case_15.json_interface,
        ),
        (
            "test_case_16",
            test_case_16.annotations,
            test_case_16.expected_json_resp,
            test_case_16.json_interface,
        ),
        (
            "test_case_17",
            test_case_17.annotations,
            test_case_17.expected_json_resp,
            test_case_17.json_interface,
        ),
        (
            "test_case_18",
            test_case_18.annotations,
            test_case_18.expected_json_resp,
            test_case_18.json_interface,
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
    json_resp = _video_annotations_to_json_response(
        annotations, json_interface=json_interface, width=1920, height=1080
    )

    # Then
    def compare_json(resp, expected) -> None:
        if isinstance(resp, dict) and isinstance(expected, dict):
            for key in resp:
                print(f"Comparing key: {key} from response with expected")
                assert key in expected, f"Key {key} not in expected"
                if key == "boundingPoly":
                    print("condition boundingPoly", resp[key])
                if (
                    key == "boundingPoly"
                    and "normalizedVertices" in resp[key][0]
                    and "normalizedVertices" in expected[key][0]
                ):
                    assert resp[key][0]["normalizedVertices"][0] == pytest.approx(
                        expected[key][0]["normalizedVertices"][0]
                    )
                else:
                    compare_json(resp[key], expected[key])
        elif isinstance(resp, list) and isinstance(expected, list):
            assert len(resp) == len(expected)
            for r, e in zip(resp, expected):
                compare_json(r, e)
        else:
            assert resp == expected

    compare_json(json_resp, expected_json_resp)


@pytest.mark.parametrize(
    ("test_case_name", "annotations", "expected_json_resp"),
    [
        (
            "test_case_14",
            test_case_14.annotations,
            test_case_14.expected_json_resp,
        ),
        (
            "test_case_19",
            test_case_19.annotations,
            test_case_19.expected_json_resp,
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
    json_resp = _classic_annotations_to_json_response(annotations, {})

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
        previous_vertices=bbox_start, next_vertices=bbox_end, weight=weight, width=1920, height=1080
    )

    # Then
    for vertice_interpolated, vertice_expected in zip(interpolated_bbox, expected_bbox):
        assert vertice_interpolated["x"] == pytest.approx(vertice_expected["x"], 1e-3)
        assert vertice_interpolated["y"] == pytest.approx(vertice_expected["y"], 1e-3)
