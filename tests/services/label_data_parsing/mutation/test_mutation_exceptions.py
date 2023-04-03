import pytest

from kili.services.label_data_parsing.exceptions import (
    AttributeNotCompatibleWithJobError,
    InvalidMutationError,
)
from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project


def test_mutate_transcription_label_on_classif_project():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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
                "isChild": False,
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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
                "required": 0,
                "isChild": False,
                "isChild": False,
            }
        }
    }

    json_response_dict = {}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

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
                "isChild": False,
                "content": {
                    "categories": {"A": {}, "B": {}},
                    "input": "radio",
                },
            }
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    bb_annotations = parsed_jobs["OBJECT_DETECTION_JOB"].annotations

    assert bb_annotations[0].category.name == "A"
    assert bb_annotations[0].mid == "20230315142306286-25528"

    with pytest.raises(AttributeNotCompatibleWithJobError):
        bb_annotations[0].begin_offset = 0

    with pytest.raises(AttributeNotCompatibleWithJobError):
        bb_annotations[0].end_offset = 42


def test_cannot_add_same_category_twice_to_categorylist_with_add_category():
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

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "A"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)

    with pytest.raises(
        InvalidMutationError,
        match=(
            "Cannot add a category with name 'A' because a category with the same name already"
            " exists"
        ),
    ):
        parsed_jobs["CLASSIFICATION_JOB"].add_category(name="A", confidence=100)


def test_add_annotation_ner_wrong_category_name():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {"ORG": {}, "PERSON": {}},
                    "input": "radio",
                },
            }
        }
    }

    json_response_dict = {
        "JOB_0": {
            "annotations": [
                {
                    "categories": [{"name": "ORG", "confidence": 42}],
                    "beginOffset": 21,
                    "content": "this is the text for Kili",
                    "mid": "a",
                },
                {
                    "categories": [{"name": "PERSON", "confidence": 100}],
                    "beginOffset": 8,
                    "content": "this is Toto's text",
                    "mid": "b",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    with pytest.raises(
        InvalidMutationError,
        match=(
            "Category 'THIS_NAME_IS_NOT_IN_THE_JSON_INTERFACE' is not in the job interface with"
            " categories"
        ),
    ):
        parsed_jobs["JOB_0"].add_annotation(
            {
                "categories": [
                    {"name": "THIS_NAME_IS_NOT_IN_THE_JSON_INTERFACE", "confidence": 59}
                ],
                "beginOffset": 42,
                "content": "this is the text for Kili",
                "mid": "c",
            }
        )


def test_set_normalized_vertices_wrong_values():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A", "color": "#733AFB"},
                        "OBJECT_B": {"children": [], "name": "Object B", "color": "#3CD876"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["semantic"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 0,
            }
        }
    }

    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [
                        {"normalizedVertices": [{"x": 0.5141441957015471, "y": 0.6164292619007603}]}
                    ],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230329145907681-18624",
                    "type": "semantic",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)
    with pytest.raises(ValueError):
        parsed_jobs["JOB_0"].annotations[0].bounding_poly[0].normalized_vertices = [
            {"x": 10000, "y": 0}
        ]


def test_add_semantic_annotation_to_bbox_job():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A", "color": "#733AFB"},
                        "OBJECT_B": {"children": [], "name": "Object B", "color": "#3CD876"},
                    },
                    "input": "checkbox",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 0,
            }
        }
    }

    json_resp = {}
    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)

    with pytest.raises(InvalidMutationError):
        parsed_jobs["JOB_0"].add_annotation(
            {
                "children": {},
                "boundingPoly": [
                    {"normalizedVertices": [{"x": 0.5141441957015471, "y": 0.6164292619007603}]},
                ],
                "categories": [{"name": "OBJECT_B"}],
                "mid": "20230329145907681-18624",
                "type": "semantic",
            }
        )


@pytest.mark.skip("TODO")
def test_mutation_transcription_with_restricted_values():
    json_interface = {
        "jobs": {
            "TRANSCRIPTION_JOB_ANY_INPUT": {
                "content": {"input": "textField"},
                "instruction": "Transcription",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": False,
            },
            "TRANSCRIPTION_JOB_NUMBER": {
                "content": {"input": "number"},
                "instruction": "Number",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": False,
            },
            "TRANSCRIPTION_JOB_DATE": {
                "content": {"input": "date"},
                "instruction": "Date",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": False,
            },
        }
    }
    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore

    # TODO: the setter should raise if value set is not compatible with input type
