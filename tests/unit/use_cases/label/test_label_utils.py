from typing import Dict, List, cast

import pytest

from kili.domain.annotation import VideoAnnotation
from kili.use_cases.label.utils import video_label_annotations_to_json_response

from .test_data import test_case_1, test_case_2, test_case_3


@pytest.mark.parametrize(
    ("annotations", "expected_json_resp"),
    [
        (test_case_1.annotations, test_case_1.expected_json_resp),
        (test_case_2.annotations, test_case_2.expected_json_resp),
        (test_case_3.annotations, test_case_3.expected_json_resp),
    ],
)
def test_given_video_label_annotations_when_converting_to_json_resp_it_works(
    annotations: List[Dict], expected_json_resp: Dict
):
    # Given
    _ = annotations

    # When
    json_resp = video_label_annotations_to_json_response(cast(List[VideoAnnotation], annotations))

    # Then
    assert json_resp == expected_json_resp
