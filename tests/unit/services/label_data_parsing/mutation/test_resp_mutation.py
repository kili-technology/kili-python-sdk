from copy import deepcopy

from typing_extensions import assert_type

from kili.services.label_data_parsing.json_response import (
    FramesList,
    JobPayload,
    ParsedJobs,
)
from kili.services.label_data_parsing.types import Project
from kili.utils.labels.parsing import ParsedLabel


def test_set_attribute_categories_multiclass():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {
                        "CATEGORY_A": {"children": [], "name": "Category A", "id": "category30"},
                        "CATEGORY_B": {"children": [], "name": "Category B", "id": "category31"},
                        "CATEGORY_C": {"children": [], "name": "Category C", "id": "category32"},
                    },
                    "input": "checkbox",
                },
            }
        }
    }

    json_response_dict = {
        "JOB_0": {
            "categories": [
                {"name": "CATEGORY_A"},
                {"name": "CATEGORY_B"},
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)
    categories = parsed_jobs["JOB_0"].categories

    assert categories[0].display_name == "Category A"
    assert categories[0].name == "CATEGORY_A"
    assert categories[1].display_name == "Category B"
    assert categories[1].name == "CATEGORY_B"

    categories[0].display_name = "Category B"
    assert categories[0].display_name == "Category B"
    assert categories[0].name == "CATEGORY_B"

    categories[1].name = "CATEGORY_A"
    assert categories[1].display_name == "Category A"
    assert categories[1].name == "CATEGORY_A"

    assert parsed_jobs.to_dict() == {
        "JOB_0": {
            "categories": [
                {"name": "CATEGORY_B"},
                {"name": "CATEGORY_A"},
            ]
        }
    }


def test_mutate_transcription_label():
    json_interface = {
        "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1, "isChild": False}}
    }

    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    assert parsed_jobs["JOB_0"].text == "This is a transcription job"

    parsed_jobs["JOB_0"].text = "This is a transcription job that has been mutated"
    assert parsed_jobs["JOB_0"].text == "This is a transcription job that has been mutated"


def test_mutate_transcription_label_non_required():
    json_interface = {
        "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 0, "isChild": False}}
    }

    json_response_dict = {}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    parsed_jobs["JOB_0"].text = "This is a transcription job"
    assert parsed_jobs["JOB_0"].text == "This is a transcription job"


def test_mutate_category():
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

    parsed_jobs["JOB_0"].category.name = "B"
    parsed_jobs["JOB_0"].category.confidence = 50

    assert parsed_jobs["JOB_0"].category.name == "B"
    assert parsed_jobs["JOB_0"].category.confidence == 50


def test_mutate_categories_radio_required():
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

    assert parsed_jobs["JOB_0"].categories[0].name == "A"
    assert parsed_jobs["JOB_0"].categories[0].confidence == 100

    parsed_jobs["JOB_0"].categories[0].name = "B"
    parsed_jobs["JOB_0"].categories[0].confidence = 50

    assert parsed_jobs["JOB_0"].categories[0].name == "B"
    assert parsed_jobs["JOB_0"].categories[0].confidence == 50


def test_mutate_category_categories_radio_required():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": "radio",
                },
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "C"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    assert parsed_jobs["JOB_0"].category.name == "C"

    parsed_jobs["JOB_0"].category.name = "B"
    parsed_jobs["JOB_0"].category.confidence = 42

    assert parsed_jobs["JOB_0"].category.name == "B"
    assert parsed_jobs["JOB_0"].category.confidence == 42
    assert parsed_jobs["JOB_0"].categories[0].name == "B"
    assert parsed_jobs["JOB_0"].categories[0].confidence == 42


def test_mutate_category_categories_radio_non_required():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                    },
                    "input": "radio",
                },
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            }
        }
    }

    json_response_dict = {}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    parsed_jobs["JOB_0"].add_category(name="A", confidence=50)

    assert parsed_jobs["JOB_0"].category.name == "A"
    assert parsed_jobs["JOB_0"].category.confidence == 50
    assert parsed_jobs["JOB_0"].categories[0].name == "A"
    assert parsed_jobs["JOB_0"].categories[0].confidence == 50


def test_mutate_categories_checkbox():
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                        "C": {"children": [], "name": "C"},
                        "D": {"children": [], "name": "D"},
                    },
                    "input": "checkbox",
                },
                "instruction": "Class",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }
    json_resp_dict = {
        "CLASSIFICATION_JOB": {
            "categories": [{"confidence": 100, "name": "A"}, {"confidence": 100, "name": "C"}]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp_dict, project_info=project_info)

    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "A"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].name == "C"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].confidence == 100

    parsed_jobs["CLASSIFICATION_JOB"].categories[0].name = "B"
    parsed_jobs["CLASSIFICATION_JOB"].add_category(name="D", confidence=50)

    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].name == "C"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[2].confidence == 50
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[2].name == "D"


def test_mutate_ner_project_entity_annotations():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {"ORG": {"name": "org"}, "PERSON": {"name": "person"}},
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

    parsed_jobs["JOB_0"].entity_annotations[0].categories[0].display_name = "person"
    parsed_jobs["JOB_0"].entity_annotations[0].categories[0].name = "PERSON"
    parsed_jobs["JOB_0"].entity_annotations[0].categories[0].confidence = 98
    parsed_jobs["JOB_0"].entity_annotations[0].begin_offset = 42
    parsed_jobs["JOB_0"].entity_annotations[0].content = "abcdef"
    parsed_jobs["JOB_0"].entity_annotations[0].mid = "new mid"

    assert parsed_jobs["JOB_0"].entity_annotations[0].category.display_name == "person"
    assert parsed_jobs["JOB_0"].entity_annotations[0].category.name == "PERSON"
    assert parsed_jobs["JOB_0"].entity_annotations[0].category.confidence == 98
    assert parsed_jobs["JOB_0"].entity_annotations[0].begin_offset == 42
    assert parsed_jobs["JOB_0"].entity_annotations[0].content == "abcdef"
    assert parsed_jobs["JOB_0"].entity_annotations[0].mid == "new mid"


def test_mutate_ner_project_annotations():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {"ORG": {"name": "org"}, "PERSON": {"name": "person"}},
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

    parsed_jobs["JOB_0"].annotations[0].categories[0].display_name = "person"
    parsed_jobs["JOB_0"].annotations[0].categories[0].name = "PERSON"
    parsed_jobs["JOB_0"].annotations[0].categories[0].confidence = 98
    parsed_jobs["JOB_0"].annotations[0].begin_offset = 42
    parsed_jobs["JOB_0"].annotations[0].content = "abcdef"
    parsed_jobs["JOB_0"].annotations[0].mid = "new mid"

    assert parsed_jobs["JOB_0"].annotations[0].category.display_name == "person"
    assert parsed_jobs["JOB_0"].annotations[0].category.name == "PERSON"
    assert parsed_jobs["JOB_0"].annotations[0].category.confidence == 98
    assert parsed_jobs["JOB_0"].annotations[0].begin_offset == 42
    assert parsed_jobs["JOB_0"].annotations[0].content == "abcdef"
    assert parsed_jobs["JOB_0"].annotations[0].mid == "new mid"


def test_mutation_single_dropdown():
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A", "id": "category14"},
                        "B": {"children": [], "name": "B", "id": "category15"},
                        "C": {"children": [], "name": "C", "id": "category16"},
                    },
                    "input": "singleDropdown",
                },
                "instruction": "Single choice dropdown",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
                "isNew": False,
            }
        }
    }
    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "A"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)

    parsed_jobs["CLASSIFICATION_JOB"].categories[0].name = "B"
    parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence = 99

    assert parsed_jobs["CLASSIFICATION_JOB"].category.name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].category.confidence == 99


def test_mutation_multiple_dropdown():
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB_0": {
                "content": {
                    "categories": {
                        "D": {"children": [], "name": "D", "id": "category17"},
                        "E": {"children": [], "name": "E", "id": "category18"},
                        "F": {"children": [], "name": "F", "id": "category19"},
                    },
                    "input": "multipleDropdown",
                },
                "instruction": "Multi choice dropdown",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
                "isNew": False,
            }
        }
    }

    json_resp = {
        "CLASSIFICATION_JOB_0": {
            "categories": [{"confidence": 100, "name": "E"}, {"confidence": 99, "name": "F"}]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)

    parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].name = "D"
    parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].confidence = 98
    parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].name = "E"
    parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].confidence = 97

    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].name == "D"
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].confidence == 98
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].name == "E"
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].confidence == 97


def test_add_annotations_to_empty_json_resp_of_non_required_job():
    json_interface = {
        "jobs": {
            "REQUIRED_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "name": "A"},
                        "B": {"children": [], "name": "B"},
                    },
                    "input": "radio",
                },
                "instruction": "Class required",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            },
            "NON_REQUIRED_JOB": {
                "content": {
                    "categories": {
                        "C": {"children": [], "name": "C"},
                        "D": {"children": [], "name": "D"},
                    },
                    "input": "radio",
                },
                "instruction": "Class non required",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            },
        }
    }

    json_resp = {"REQUIRED_JOB": {"categories": [{"confidence": 100, "name": "A"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_resp, project_info=project_info)

    parsed_jobs["NON_REQUIRED_JOB"].add_category("C", 100)

    assert parsed_jobs["NON_REQUIRED_JOB"].categories[0].name == "C"


def test_add_annotation_ner():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
                "content": {
                    "categories": {"ORG": {"name": "org"}, "PERSON": {"name": "person"}},
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

    parsed_jobs["JOB_0"].add_annotation(
        {
            "categories": [{"name": "ORG", "confidence": 59}],
            "beginOffset": 42,
            "content": "this is the text for Kili",
            "mid": "c",
        }
    )

    assert parsed_jobs["JOB_0"].annotations[2].categories[0].display_name == "org"
    assert parsed_jobs["JOB_0"].annotations[2].categories[0].name == "ORG"
    assert parsed_jobs["JOB_0"].annotations[2].categories[0].confidence == 59
    assert parsed_jobs["JOB_0"].annotations[2].begin_offset == 42
    assert parsed_jobs["JOB_0"].annotations[2].content == "this is the text for Kili"
    assert parsed_jobs["JOB_0"].annotations[2].mid == "c"

    assert parsed_jobs["JOB_0"].annotations[0].begin_offset == 21
    assert parsed_jobs["JOB_0"].annotations[1].begin_offset == 8


def test_set_normalized_vertices():
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

    parsed_jobs["JOB_0"].annotations[0].bounding_poly[0].normalized_vertices = [
        {"x": 0.5, "y": 0.5}
    ]

    assert parsed_jobs["JOB_0"].annotations[0].bounding_poly[0].normalized_vertices[0] == {
        "x": 0.5,
        "y": 0.5,
    }


def test_add_category_in_annotation_bbox():
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

    parsed_jobs["JOB_0"].add_annotation(
        {
            "children": {},
            "boundingPoly": [
                {
                    "normalizedVertices": [
                        {"x": 0.5141441957015471, "y": 0.6164292619007603},
                        {"x": 0.5141441957015471, "y": 0.6164292619007603},
                        {"x": 0.5141441957015471, "y": 0.6164292619007603},
                        {"x": 0.5141441957015471, "y": 0.6164292619007603},
                    ]
                },
            ],
            "categories": [{"name": "OBJECT_B"}],
            "mid": "20230329145907681-18624",
            "type": "rectangle",
        }
    )

    assert parsed_jobs["JOB_0"].annotations[0].categories[0].display_name == "Object B"
    assert parsed_jobs["JOB_0"].annotations[0].categories[0].name == "OBJECT_B"

    parsed_jobs["JOB_0"].annotations[0].add_category("OBJECT_A", 100)

    assert parsed_jobs["JOB_0"].annotations[0].categories[1].display_name == "Object A"
    assert parsed_jobs["JOB_0"].annotations[0].categories[1].name == "OBJECT_A"


def test_add_bounding_poly():
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
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 0,
            }
        }
    }

    point = {"x": 0.5, "y": 0.5}
    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": [point] * 4}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230405103955940-26928",
                    "type": "rectangle",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=deepcopy(json_resp), project_info=project_info)

    parsed_jobs["JOB_0"].bounding_poly_annotations[0].add_bounding_poly(
        {"normalizedVertices": [point, point, point, point]}  # type: ignore
    )

    assert parsed_jobs.to_dict() == {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [
                        {"normalizedVertices": [point] * 4},
                        {"normalizedVertices": [point] * 4},
                    ],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230405103955940-26928",
                    "type": "rectangle",
                }
            ]
        }
    }


def test_video_project_set_score():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Train", "color": "#733AFB"},
                        "OBJECT_B": {"children": [], "name": "Car", "color": "#3CD876"},
                    },
                    "input": "radio",
                },
                "instruction": "Track objects A and B",
                "isChild": False,
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {"tracking": {}},
                "isVisible": True,
                "required": 0,
            },
        }
    }

    json_resp = {
        "0": {},
        "1": {
            "JOB_0": {
                "annotations": [
                    {
                        "children": {},
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {"x": 0.3046607129483673, "y": 0.6337517633095981},
                                    {"x": 0.3046607129483673, "y": 0.5534349836511678},
                                    {"x": 0.3670709937679789, "y": 0.5534349836511678},
                                    {"x": 0.3670709937679789, "y": 0.6337517633095981},
                                ]
                            }
                        ],
                        "categories": [{"name": "OBJECT_B"}],
                        "mid": "20230407140827577-43802",
                        "type": "rectangle",
                        "isKeyFrame": True,
                    },
                ]
            }
        },
    }

    label = {"jsonResponse": json_resp}

    parsed_label = ParsedLabel(label=label, json_interface=json_interface, input_type="VIDEO")

    job_payload = parsed_label.jobs["JOB_0"]
    assert_type(job_payload, JobPayload)
    assert_type(job_payload.frames, FramesList)

    assert len(parsed_label.jobs["JOB_0"].frames) == 2

    frame = parsed_label.jobs["JOB_0"].frames[1]

    assert frame.annotations[0].score is None
    frame.annotations[0].score = 42
    assert frame.annotations[0].score == 42

    label_as_dict = parsed_label.to_dict()
    assert label_as_dict == {
        "jsonResponse": {
            "0": {},
            "1": {
                "JOB_0": {
                    "annotations": [
                        {
                            "children": {},
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.3046607129483673, "y": 0.6337517633095981},
                                        {"x": 0.3046607129483673, "y": 0.5534349836511678},
                                        {"x": 0.3670709937679789, "y": 0.5534349836511678},
                                        {"x": 0.3670709937679789, "y": 0.6337517633095981},
                                    ]
                                }
                            ],
                            "categories": [{"name": "OBJECT_B"}],
                            "mid": "20230407140827577-43802",
                            "type": "rectangle",
                            "isKeyFrame": True,
                            "score": 42,
                        },
                    ]
                }
            },
        }
    }
