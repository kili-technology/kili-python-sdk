import pytest

from kili.services.json_response.exceptions import (
    AttributeNotCompatibleWithJobError,
    JobNotExistingError,
)
from kili.services.json_response.json_response import ParsedJobs


def test_attribute_category_checkbox_job():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {"categories": {"A": {}}, "input": "checkbox"},
                "mlTask": "CLASSIFICATION",
                "required": 0,
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"name": "A"}]}}
    parsed_jobs = ParsedJobs(json_response_dict, json_interface)
    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].category


def test_job_not_existing_error():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {"jobs": {"JOB_0": {"required": 1}}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    with pytest.raises(JobNotExistingError):
        _ = parsed_jobs["JOB_000000000"].text


def test_attribute_not_compatible_with_transcription_job_error():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].text == "This is a transcription job"

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].categories

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].entity_annotations


def test_attribute_not_compatible_with_classif_job_error():
    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A", "id": "category30"},
                        "B": {"children": [], "name": "B", "id": "category31"},
                        "C": {"children": [], "name": "C", "id": "category32"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].category.name == "A"
    assert parsed_jobs["JOB_0"].category.confidence == 100

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].text

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].entity_annotations


def test_query_invalid_attributes_on_bbox_annotations():
    json_response_dict = {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.5399158345838302, "y": 0.5232713051936337},
                                {"x": 0.5399158345838302, "y": 0.3366534157113883},
                                {"x": 0.7009885775980994, "y": 0.3366534157113883},
                                {"x": 0.7009885775980994, "y": 0.5232713051936337},
                            ]
                        }
                    ],
                    "categories": [{"name": "A"}],
                    "mid": "20230315142306286-25528",
                    "type": "rectangle",
                }
            ]
        }
    }
    json_interface = {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "required": 1,
                "content": {
                    "categories": {"A": {}, "B": {}},
                    "input": "radio",
                },
            }
        }
    }

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    bb_annotations = parsed_jobs["OBJECT_DETECTION_JOB"].annotations

    assert bb_annotations[0].category.name == "A"
    assert bb_annotations[0].mid == "20230315142306286-25528"

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].begin_offset

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].bounding_polygon

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].is_key_frame

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].end_offset

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].point

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].points

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].kind
