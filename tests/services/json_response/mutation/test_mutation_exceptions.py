import pytest

from kili.services.json_response.exceptions import (
    AttributeNotCompatibleWithJobError,
    InvalidMutationError,
)
from kili.services.json_response.json_response import ParsedJobs


def test_mutate_transcription_label_on_classif_project():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A", "id": "category25"},
                        "B": {"children": [], "name": "B", "id": "category26"},
                        "C": {"children": [], "name": "C", "id": "category27"},
                    },
                    "input": "radio",
                },
            }
        }
    }
    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].category.name == "A"

    with pytest.raises(AttributeNotCompatibleWithJobError):
        _ = parsed_jobs["JOB_0"].text

    with pytest.raises(AttributeNotCompatibleWithJobError):
        parsed_jobs["JOB_0"].text = "abcdef"


@pytest.mark.parametrize("input_", ["radio", "singleDropdown"])
def test_mutate_category_label_wrong_confidence_range(input_):
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A", "id": "category25"},
                        "B": {"children": [], "name": "B", "id": "category26"},
                        "C": {"children": [], "name": "C", "id": "category27"},
                    },
                    "input": input_,
                },
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].category.name == "A"

    with pytest.raises(ValueError):
        parsed_jobs["JOB_0"].category.confidence = 101

    with pytest.raises(ValueError):
        parsed_jobs["JOB_0"].category.confidence = -1


@pytest.mark.parametrize("input_", ["radio", "singleDropdown"])
def test_mutate_single_class_classif_add_multiple_categories(input_):
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": input_,
                },
                "instruction": "Class",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].category.name == "A"

    with pytest.raises(InvalidMutationError, match="Cannot add more than one category"):
        parsed_jobs["JOB_0"].add_category(name="B", confidence=50)


@pytest.mark.parametrize("input_", ["checkbox", "multipleDropdown"])
def test_mutate_multi_class_classif_add_too_many_categories(input_):
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": input_,
                },
                "instruction": "Class",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    json_response_dict = {}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    parsed_jobs["JOB_0"].add_category(name="A", confidence=1)
    parsed_jobs["JOB_0"].add_category(name="B", confidence=2)
    parsed_jobs["JOB_0"].add_category(name="C", confidence=3)

    assert parsed_jobs["JOB_0"].categories[0].name == "A"
    assert parsed_jobs["JOB_0"].categories[0].confidence == 1
    assert parsed_jobs["JOB_0"].categories[1].name == "B"
    assert parsed_jobs["JOB_0"].categories[1].confidence == 2
    assert parsed_jobs["JOB_0"].categories[2].name == "C"
    assert parsed_jobs["JOB_0"].categories[2].confidence == 3

    with pytest.raises(InvalidMutationError, match="Cannot add more categories"):
        parsed_jobs["JOB_0"].add_category(name="A", confidence=4)


@pytest.mark.parametrize("input_", ["radio", "singleDropdown"])
def test_mutate_category_wrong_class_name(input_):
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": input_,
                },
                "instruction": "Class",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].category.name == "A"

    with pytest.raises(InvalidMutationError):
        parsed_jobs["JOB_0"].category.name = "THIS CLASS IS INVALID"


def test_invalid_mutation_on_bbox_annotations():
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
        bb_annotations[0].begin_offset = 0

    with pytest.raises(AttributeNotCompatibleWithJobError):
        bb_annotations[0].end_offset = 42
