from typing import Dict, List

import pytest

from kili.adapters.kili_api_gateway.label.annotation_to_json_response import (
    _video_label_annotations_to_json_response,
)
from kili.domain.annotation import VideoAnnotation

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
    json_resp = _video_label_annotations_to_json_response(
        annotations, json_interface=json_interface
    )

    # Then
    assert json_resp == expected_json_resp
