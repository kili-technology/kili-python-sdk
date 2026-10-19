import pytest
from kili_formats.tool.annotations_to_json_response import (
    AnnotationsToJsonResponseConverter,
)
from kili_formats.types import ClassicAnnotation

from .test_data import (
    test_case_14,
    test_case_19,
)


@pytest.mark.parametrize(
    ("test_case_name", "annotations", "expected_json_resp", "json_interface"),
    [
        (
            "test_case_14",
            test_case_14.annotations,
            test_case_14.expected_json_resp,
            test_case_14.json_interface,
        ),
        (
            "test_case_19",
            test_case_19.annotations,
            test_case_19.expected_json_resp,
            test_case_19.json_interface,
        ),
    ],
)
def test_given_llm_label_annotations_when_converting_to_json_resp_it_works(
    test_case_name: str,
    annotations: list[ClassicAnnotation],
    expected_json_resp: dict,
    json_interface: dict,
):
    # Given
    label = {"jsonResponse": {}}
    converter = AnnotationsToJsonResponseConverter(
        json_interface=json_interface, project_input_type="LLM_STATIC"
    )

    # When
    converter.patch_label_json_response(None, label, annotations)

    # Then
    assert label["jsonResponse"] == expected_json_resp
