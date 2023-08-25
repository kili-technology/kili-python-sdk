import pytest

from kili.services.label_data_parsing.exceptions import (
    AttributeNotCompatibleWithJobError,
    InvalidMutationError,
    JobNotExistingError,
)
from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project


def test_attribute_category_checkbox_job():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {"categories": {"A": {"name": "a"}}, "input": "checkbox"},
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"name": "A"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)
    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].category


def test_job_not_existing_error():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {"jobs": {"JOB_0": {"required": 1, "isChild": False}}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    with pytest.raises(JobNotExistingError):
        _ = parsed_jobs["JOB_000000000"].text


def test_attribute_not_compatible_with_transcription_job_error():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {
        "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1, "isChild": False}}
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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
                "isChild": False,
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    assert parsed_jobs["JOB_0"].category.name == "A"
    assert parsed_jobs["JOB_0"].category.confidence == 100

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].text

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].entity_annotations


def test_query_invalid_attributes_on_bbox_annotations():
    json_interface = {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {"A": {"name": "a"}, "B": {"name": "b"}},
                    "input": "radio",
                },
            }
        }
    }
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    bb_annotations = parsed_jobs["OBJECT_DETECTION_JOB"].annotations

    assert bb_annotations[0].category.display_name == "a"
    assert bb_annotations[0].category.name == "A"
    assert bb_annotations[0].mid == "20230315142306286-25528"

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = bb_annotations[0].begin_offset

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


def test_access_bounding_poly_on_point_job():
    json_interface = {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "color": "#472CED", "name": "A"},
                        "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                    },
                    "input": "radio",
                },
                "instruction": "Class",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["marker"],
                "isChild": False,
            }
        }
    }

    point = {"x": 0.5578332680516701, "y": 0.2630529867187432}

    json_resp = {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "point": point,
                    "categories": [{"name": "A"}],
                    "mid": "20230323113855529-11197",
                    "type": "marker",
                },
                {
                    "children": {},
                    "point": point,
                    "categories": [{"name": "B"}],
                    "mid": "20230323113857016-51829",
                    "type": "marker",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)
    job = parsed_jobs["OBJECT_DETECTION_JOB"]

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = job.annotations[0].bounding_poly


def test_cannot_add_same_category_twice_to_categorylist():
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": "checkbox",
                },
                "instruction": "Category",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    json_resp = {
        "CLASSIFICATION_JOB": {
            "categories": [
                {"confidence": 100, "name": "A"},
                {"confidence": 100, "name": "A"},  # duplicate category
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore

    with pytest.raises(
        InvalidMutationError,
        match=(
            "Cannot add a category with name 'A' because a category with the same name already"
            " exists"
        ),
    ):
        _ = ParsedJobs(json_response=json_resp, project_info=project_info)
