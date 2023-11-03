from typing import Dict, List, cast

import pytest

from kili.domain.annotation import Vertice, VideoAnnotation
from kili.use_cases.label.utils import (
    _interpolate_object_,
    video_label_annotations_to_json_response,
)

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
    ],
)
def test_given_video_label_annotations_when_converting_to_json_resp_it_works(
    test_case_name: str, annotations: List[Dict], expected_json_resp: Dict, json_interface: Dict
):
    # Given
    _ = annotations

    # When
    json_resp = video_label_annotations_to_json_response(
        cast(List[VideoAnnotation], annotations), json_interface=json_interface
    )

    # Then
    assert json_resp == expected_json_resp


@pytest.mark.parametrize(
    (
        "test_case_name",
        "bbox_start",
        "frame_start_index",
        "bbox_end",
        "frame_end_index",
        "expected_bboxes",
    ),
    [
        (
            "same bbox on two consecutive frames",
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            0,
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            1,
            [],
        ),
        (
            "same bbox, one bbox frame to generate in between",
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            0,
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            2,
            [
                [
                    {"x": 0.012, "y": 0.077},  # bottom left
                    {"x": 0.012, "y": 0.030},  # top left
                    {"x": 0.223, "y": 0.030},  # top right
                    {"x": 0.223, "y": 0.077},  # bottom right
                ]
            ],
        ),
        (
            "bbox shifted right, one bbox frame to generate in between",
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            0,
            [
                {"x": 0.012 + 0.5, "y": 0.077},  # bottom left
                {"x": 0.012 + 0.5, "y": 0.030},  # top left
                {"x": 0.223 + 0.5, "y": 0.030},  # top right
                {"x": 0.223 + 0.5, "y": 0.077},  # bottom right
            ],
            2,
            [
                [
                    {"x": 0.012 + 0.25, "y": 0.077},  # bottom left
                    {"x": 0.012 + 0.25, "y": 0.030},  # top left
                    {"x": 0.223 + 0.25, "y": 0.030},  # top right
                    {"x": 0.223 + 0.25, "y": 0.077},  # bottom right
                ]
            ],
        ),
        (
            "bbox shifted right, two bbox frames to generate in between",
            [
                {"x": 0.012, "y": 0.077},  # bottom left
                {"x": 0.012, "y": 0.030},  # top left
                {"x": 0.223, "y": 0.030},  # top right
                {"x": 0.223, "y": 0.077},  # bottom right
            ],
            0,
            [
                {"x": 0.012 + 0.3, "y": 0.077},  # bottom left
                {"x": 0.012 + 0.3, "y": 0.030},  # top left
                {"x": 0.223 + 0.3, "y": 0.030},  # top right
                {"x": 0.223 + 0.3, "y": 0.077},  # bottom right
            ],
            3,
            [
                [
                    {"x": 0.012 + 0.1, "y": 0.077},  # bottom left
                    {"x": 0.012 + 0.1, "y": 0.030},  # top left
                    {"x": 0.223 + 0.1, "y": 0.030},  # top right
                    {"x": 0.223 + 0.1, "y": 0.077},  # bottom right
                ],
                [
                    {"x": 0.012 + 0.2, "y": 0.077},  # bottom left
                    {"x": 0.012 + 0.2, "y": 0.030},  # top left
                    {"x": 0.223 + 0.2, "y": 0.030},  # top right
                    {"x": 0.223 + 0.2, "y": 0.077},  # bottom right
                ],
            ],
        ),
        (
            "bbox vertical top left, ending box horizontal top, one bbox frame to generate",
            [
                {"x": 0.0026680473764734273, "y": 0.3115594847386215},
                {"x": 0.0026680473764734273, "y": 0.003480142312792922},
                {"x": 0.12273017931777766, "y": 0.003480142312792922},
                {"x": 0.12273017931777766, "y": 0.3115594847386215},
            ],
            0,
            [
                {"x": 0.0026680473764734273, "y": 0.502273186857896},
                {"x": 0.0026680473764734273, "y": 0.003480142312792922},
                {"x": 0.9951816714245885, "y": 0.003480142312792922},
                {"x": 0.9951816714245885, "y": 0.502273186857896},
            ],
            2,
            [
                [
                    {"x": 0.0026680473764734815, "y": 0.4069163357982587},  # bottom left
                    {"x": 0.0026680473764734815, "y": 0.0034801423127929},  # top left
                    {"x": 0.5589559253711831, "y": 0.0034801423127929},  # top right
                    {"x": 0.5589559253711831, "y": 0.4069163357982587},  # bottom right
                ],
            ],
        ),
    ],
)
def test_given_two_bboxes_on_different_frames_when_generating_intermediate_bboxes_it_works(
    test_case_name: str,
    bbox_start: List[Vertice],
    frame_start_index: int,
    bbox_end: List[Vertice],
    frame_end_index: int,
    expected_bboxes: List[List[Vertice]],
):
    # Given

    # When
    generated_bboxes = []
    for frame_id in range(frame_start_index + 1, frame_end_index):
        generated_bboxes.append(
            _interpolate_object_(
                object_initial_state=bbox_start,
                object_final_state=bbox_end,
                initial_state_frame_index=frame_start_index,
                final_state_frame_index=frame_end_index,
                at_frame=frame_id,
            )
        )

    # Then
    for generated_bbox, expected_bbox in zip(generated_bboxes, expected_bboxes):
        for generated_vertice, expected_vertice in zip(generated_bbox, expected_bbox):
            assert generated_vertice["x"] == pytest.approx(expected_vertice["x"])
            assert generated_vertice["y"] == pytest.approx(expected_vertice["y"])
