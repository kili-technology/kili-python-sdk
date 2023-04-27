from copy import deepcopy

import pytest

from kili.services.label_data_parsing.annotation import (
    Annotation,
    AnnotationList,
    BoundingPolyAnnotation,
)
from kili.services.label_data_parsing.bounding_poly import BoundingPoly
from kili.services.label_data_parsing.category import Category, CategoryList
from kili.services.label_data_parsing.exceptions import FrameIndexError
from kili.services.label_data_parsing.job_response import JobPayload
from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project
from kili.utils.labels.label_parsing import ParsedLabel


def test_attribute_category():
    json_response_dict = {
        "JOB_0": {
            "categories": [
                {
                    "confidence": 100,
                    "name": "A",
                }
            ]
        }
    }
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "isChild": False,
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)
    category = parsed_jobs["JOB_0"].category

    assert parsed_jobs["JOB_0"].categories[0].name == category.name == "A"
    assert parsed_jobs["JOB_0"].categories[0].confidence == category.confidence == 100


def test_attribute_categories_multiclass():
    json_response_dict = {
        "JOB_0": {
            "categories": [
                {"name": "A", "confidence": 42},
                {"name": "B", "confidence": 100},
            ]
        }
    }
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
                    "input": "checkbox",
                },
            }
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)
    categories = parsed_jobs["JOB_0"].categories

    assert categories[0].confidence == 42
    assert categories[0].name == "A"
    assert categories[1].confidence == 100
    assert categories[1].name == "B"


def test_attribute_text():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {
        "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1, "isChild": False}}
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    assert parsed_jobs["JOB_0"].text == "This is a transcription job"


def test_attribute_entity_annotations():
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_response_dict)

    assert parsed_jobs["JOB_0"].entity_annotations[0].begin_offset == 21
    assert parsed_jobs["JOB_0"].entity_annotations[0].content == "this is the text for Kili"
    assert parsed_jobs["JOB_0"].entity_annotations[0].mid == "a"

    category = parsed_jobs["JOB_0"].entity_annotations[0].category
    categories = parsed_jobs["JOB_0"].entity_annotations[0].categories

    assert category.name == categories[0].name == "ORG"
    assert category.confidence == categories[0].confidence == 42

    assert parsed_jobs["JOB_0"].entity_annotations[1].category.name == "PERSON"
    assert parsed_jobs["JOB_0"].entity_annotations[1].category.confidence == 100


def test_attribute_object_detection():
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
                    "categories": [{"name": "B"}],
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
                "content": {"categories": {"A": {}, "B": {}}, "input": "radio"},
            }
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(json_response=json_response_dict, project_info=project_info)

    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].category.name == "B"
    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].categories[0].name == "B"
    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].mid == "20230315142306286-25528"
    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].type == "rectangle"


def test_not_required_job_classification_category_returns_none():
    json_interface = {
        "jobs": {
            "CLASSIFICATION_JOB": {
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

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    category = parsed_jobs["CLASSIFICATION_JOB"].category
    assert category.name == "B"
    assert category.confidence == 100

    json_resp = {}  # asset annotated but no category chosen
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    assert parsed_jobs["CLASSIFICATION_JOB"].category is None


def test_checkbox_job_categories_required():
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
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            }
        }
    }

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100


def test_checkbox_job_categories_not_required():
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
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            }
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100

    json_resp = {
        "CLASSIFICATION_JOB": {
            "categories": [{"confidence": 100, "name": "B"}, {"confidence": 52, "name": "A"}]
        }
    }
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].name == "A"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].confidence == 52

    json_resp = {}  # asset annotated but no classes chosen
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    assert len(parsed_jobs["CLASSIFICATION_JOB"].categories) == 0


def test_single_dropdown():
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
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert parsed_jobs["CLASSIFICATION_JOB"].category.name == "A"
    assert parsed_jobs["CLASSIFICATION_JOB"].category.confidence == 100
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "A"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100


def test_multiple_dropdown():
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
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].name == "E"
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[0].confidence == 100
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].name == "F"
    assert parsed_jobs["CLASSIFICATION_JOB_0"].categories[1].confidence == 99


def test_bounding_poly_annotations():
    json_interface = {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "color": "#472CED", "name": "A"},
                        "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                        "C": {"children": [], "name": "C", "color": "#D33BCE"},
                    },
                    "input": "radio",
                },
                "instruction": "Class",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["rectangle"],
                "isChild": False,
            }
        }
    }

    vertices = [
        {"x": 0.1, "y": 0.2},
        {"x": 0.3, "y": 0.4},
        {"x": 0.5, "y": 0.6},
        {"x": 0.7, "y": 0.8},
    ]

    json_resp = {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": vertices}],
                    "categories": [{"name": "A"}],
                    "mid": "20230323105350648-87611",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": vertices}],
                    "categories": [{"name": "B"}],
                    "mid": "20230323105354831-76494",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": vertices}],
                    "categories": [{"name": "C"}],
                    "mid": "20230323105356247-63177",
                    "type": "rectangle",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    bb_annotations = parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations

    assert bb_annotations[0].category.name == bb_annotations[0].categories[0].name == "A"
    assert bb_annotations[1].category.name == bb_annotations[1].categories[0].name == "B"
    assert bb_annotations[2].category.name == bb_annotations[2].categories[0].name == "C"

    assert bb_annotations[0].type == "rectangle"
    assert bb_annotations[1].type == "rectangle"
    assert bb_annotations[2].type == "rectangle"

    assert bb_annotations[0].mid == "20230323105350648-87611"

    my_parsed_job = parsed_jobs["OBJECT_DETECTION_JOB"]

    assert isinstance(my_parsed_job.bounding_poly_annotations[0].bounding_poly[0], BoundingPoly)
    assert isinstance(my_parsed_job.annotations[0].bounding_poly[0], BoundingPoly)

    assert (
        my_parsed_job.bounding_poly_annotations[0].bounding_poly[0].normalized_vertices == vertices
    )


def test_point_job():
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
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    job = parsed_jobs["OBJECT_DETECTION_JOB"]

    assert job.annotations[0].categories[0].name == "A"

    assert job.annotations[1].type == "marker"

    assert job.annotations[1].point == point


def test_multiple_bounding_poly():
    """Most of the time bounddingPoly will be a list of one element,
    but it can be more for segmentation jobs."""
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
                "models": {"interactive-segmentation": {}},
                "isVisible": True,
                "required": 1,
            }
        }
    }

    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    # two boundingPoly objects, one for the overall object
                    # and another for a sub-object within it.
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.329233, "y": 0.40562844444444446},
                                {"x": 0.330521, "y": 0.4147928888888889},
                                {"x": 0.33181, "y": 0.4239591111111112},
                            ]
                        },
                        {
                            "normalizedVertices": [
                                {"x": 0.407836, "y": 0.3552195555555556},
                                {"x": 0.40848, "y": 0.32428622222222225},
                                {"x": 0.40848, "y": 0.358656},
                            ]
                        },
                    ],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230328091918410-41552",
                    "type": "semantic",
                },
                {
                    "children": {},
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.693257, "y": 0.2417991111111112},
                                {"x": 0.693901, "y": 0.2417991111111112},
                                {"x": 0.718384, "y": 0.24409066666666668},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230328091944201-27950",
                    "type": "semantic",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    job = parsed_jobs["JOB_0"]

    assert job.annotations[0].categories[0].name == "OBJECT_A"
    assert job.annotations[1].category.name == "OBJECT_B"

    assert job.annotations[0].type == job.annotations[1].type == "semantic"

    assert job.annotations[0].bounding_poly[0].normalized_vertices[0]
    assert job.annotations[0].bounding_poly[1].normalized_vertices[0]
    assert job.annotations[1].bounding_poly[0].normalized_vertices[0]


def test_text_ner_job_with_relation_job():
    json_interface = {
        "jobs": {
            "RECOGNITION_JOB": {
                "content": {
                    "categories": {
                        "INTERJECTION": {
                            "children": [],
                            "name": "Interjection",
                            "color": "#733AFB",
                        },
                        "NOUN": {"children": [], "name": "Noun", "color": "#3CD876"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "models": {},
                "isVisible": False,
                "required": 1,
            },
            "RELATION_JOB": {
                "content": {
                    "categories": {
                        "CATEGORY_RELATION_JOB": {
                            "children": [],
                            "color": "#472CED",
                            "name": "Category relation job",
                            "startEntities": ["INTERJECTION"],
                            "endEntities": ["NOUN"],
                        }
                    },
                    "input": "radio",
                },
                "instruction": "relation job",
                "mlTask": "NAMED_ENTITIES_RELATION",
                "required": 1,
                "isChild": False,
            },
        }
    }

    json_resp = {
        "RECOGNITION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "beginId": "main/[0]",
                    "beginOffset": 157,
                    "categories": [{"name": "INTERJECTION"}],
                    "content": "Cras",
                    "endId": "main/[0]",
                    "endOffset": 161,
                    "mid": "20230328130206104-77794",
                },
                {
                    "children": {},
                    "beginId": "main/[0]",
                    "beginOffset": 172,
                    "categories": [{"name": "NOUN"}],
                    "content": "ultrices",
                    "endId": "main/[0]",
                    "endOffset": 180,
                    "mid": "20230328130207923-16649",
                },
            ]
        },
        "RELATION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "categories": [{"name": "CATEGORY_RELATION_JOB"}],
                    "endEntities": [{"mid": "20230328130207923-16649"}],
                    "mid": "20230328130209721-25195",
                    "startEntities": [{"mid": "20230328130206104-77794"}],
                }
            ]
        },
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)
    relation_job = parsed_jobs["RELATION_JOB"]

    assert relation_job.annotations[0].categories[0].name == "CATEGORY_RELATION_JOB"
    assert relation_job.annotations[0].start_entities[0]
    assert relation_job.annotations[0].end_entities[0]


def test_object_detection_with_relations():
    json_interface = {
        "jobs": {
            "BBOX_JOB": {
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
                "required": 1,
            },
            "OBJECT_RELATION_JOB": {
                "content": {
                    "categories": {
                        "CATEGORY_A": {
                            "children": [],
                            "color": "#472CED",
                            "name": "Category A",
                            "startObjects": ["OBJECT_B"],
                            "endObjects": ["OBJECT_A"],
                        }
                    },
                    "input": "radio",
                },
                "instruction": "Relation job",
                "mlTask": "OBJECT_RELATION",
                "required": 1,
                "isChild": False,
            },
        }
    }
    bbox_vertices = [
        {"x": 0.7222501796759829, "y": 0.3872972752383619},
        {"x": 0.7222501796759829, "y": 0.20628300577506686},
        {"x": 0.8433768824227134, "y": 0.20628300577506686},
        {"x": 0.8433768824227134, "y": 0.3872972752383619},
    ]
    json_resp = {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230328131236919-30609",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230328131238225-99999",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230328131309516-20566",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230328131311855-1920",
                    "type": "rectangle",
                },
            ]
        },
        "OBJECT_RELATION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "categories": [{"name": "CATEGORY_A"}],
                    "endObjects": [{"mid": "20230328131236919-30609"}],
                    "mid": "20230328131252526-80405",
                    "startObjects": [{"mid": "20230328131238225-99999"}],
                },
                {
                    "children": {},
                    "categories": [{"name": "CATEGORY_A"}],
                    "endObjects": [{"mid": "20230328131236919-30609"}],
                    "mid": "20230328131316328-68930",
                    "startObjects": [{"mid": "20230328131309516-20566"}],
                },
            ]
        },
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    relation_job = parsed_jobs["OBJECT_RELATION_JOB"]

    assert relation_job.annotations[0].categories[0].name == "CATEGORY_A"
    assert relation_job.annotations[0].start_objects[0]
    assert relation_job.annotations[0].end_objects[0]
    assert relation_job.annotations[0].mid == "20230328131252526-80405"


def test_repr_str_custom_classes():
    json_response_dict = {
        "JOB_0": {
            "annotations": [
                {
                    "categories": [{"name": "ORG", "confidence": 42}],
                    "beginOffset": 21,
                    "content": "this is the text for Kili",
                    "mid": "a",
                }
            ]
        }
    }
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
                "content": {"categories": {"ORG": {}, "PERSON": {}}, "input": "radio"},
            }
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_response_dict)

    assert "object at 0x" not in str(parsed_jobs["JOB_0"].annotations)
    assert "object at 0x" not in repr(parsed_jobs["JOB_0"].annotations)

    assert "object at 0x" not in str(parsed_jobs["JOB_0"].annotations[0].categories)
    assert "object at 0x" not in repr(parsed_jobs["JOB_0"].annotations[0].categories)

    assert "object at 0x" not in str(parsed_jobs["JOB_0"].annotations[0].categories[0])
    assert "object at 0x" not in repr(parsed_jobs["JOB_0"].annotations[0].categories[0])


def test_annotations_empty_json_resp_non_required_job():
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

    json_resp = {}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert len(parsed_jobs["JOB_0"].annotations) == 0


def test_parsing_category_only_name():
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

    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.5141441957015471, "y": 0.6164292619007603},
                                {"x": 0.5141441957015471, "y": 0.367821056372058},
                                {"x": 0.7138743970392409, "y": 0.367821056372058},
                                {"x": 0.7138743970392409, "y": 0.6164292619007603},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230329145907681-18624",
                    "type": "rectangle",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert parsed_jobs["JOB_0"].annotations[0].categories[0].name == "OBJECT_B"

    parsed_jobs["JOB_0"].annotations[0].categories[0].name = "OBJECT_A"
    parsed_jobs["JOB_0"].annotations[0].categories[0].confidence = 42

    assert parsed_jobs["JOB_0"].annotations[0].categories[0].name == "OBJECT_A"
    assert parsed_jobs["JOB_0"].annotations[0].category.confidence == 42


def test_video_project_classification():
    json_interface = {
        "jobs": {
            "FRAME_CLASSIF_JOB": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A"},
                        "OBJECT_B": {"children": [], "name": "Object B"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": False,
                "required": 1,
            }
        }
    }

    json_resp = {
        "0": {},
        "1": {},
        "2": {},
        "3": {},
        "4": {},
        "5": {
            "FRAME_CLASSIF_JOB": {
                "categories": [{"confidence": 100, "name": "OBJECT_A"}],
                "isKeyFrame": True,
                "annotations": [],
            }
        },
        "6": {
            "FRAME_CLASSIF_JOB": {
                "categories": [{"confidence": 42, "name": "OBJECT_B"}],
                "isKeyFrame": False,
                "annotations": [],
            }
        },
        "7": {},
        "8": {},
    }

    label = {"jsonResponse": json_resp}

    parsed_label = ParsedLabel(label=label, json_interface=json_interface, input_type="VIDEO")

    assert len(parsed_label.jobs["FRAME_CLASSIF_JOB"].frames) == 9
    assert not hasattr(parsed_label, "frames")

    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[5].is_key_frame is True
    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[5].category.name == "OBJECT_A"
    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[5].category.confidence == 100

    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[6].is_key_frame is False
    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[6].category.name == "OBJECT_B"
    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[6].category.confidence == 42

    for i, frame in enumerate(parsed_label.jobs["FRAME_CLASSIF_JOB"].frames):
        if i == 5:
            frame.category.name = "OBJECT_A"
            frame.category.confidence = 100
        elif i == 6:
            frame.category.name = "OBJECT_B"
            frame.category.confidence = 42

    assert parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[0].to_dict() == {}

    with pytest.raises(
        FrameIndexError, match="Frame index 999999999 out of range for frame list of size 9."
    ):
        _ = parsed_label.jobs["FRAME_CLASSIF_JOB"].frames[999999999]

    assert parsed_label.to_dict() == label


def test_video_project_object_detection():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": ["JOB_1"], "name": "Train", "color": "#733AFB"},
                        "OBJECT_B": {"children": ["JOB_2"], "name": "Car", "color": "#3CD876"},
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
            "JOB_1": {
                "content": {
                    "categories": {
                        "IS_THE OBJECT OCCLUDED?": {
                            "children": [],
                            "name": "Is the object occluded?",
                        }
                    },
                    "input": "checkbox",
                },
                "instruction": "",
                "isChild": True,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 0,
            },
            "JOB_2": {
                "content": {
                    "categories": {
                        "IS_THE OBJECT OCCLUDED?": {
                            "children": [],
                            "name": "Is the object occluded?",
                        }
                    },
                    "input": "checkbox",
                },
                "instruction": "",
                "isChild": True,
                "mlTask": "CLASSIFICATION",
                "models": {},
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
                    {
                        "children": {
                            "JOB_1": {
                                "categories": [
                                    {"confidence": 100, "name": "IS_THE OBJECT OCCLUDED?"}
                                ],
                                "isKeyFrame": False,
                            }
                        },
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {"x": 0.22829023773489518, "y": 0.5694983395828539},
                                    {"x": 0.22829023773489518, "y": 0.5213082717877957},
                                    {"x": 0.2750979483496039, "y": 0.5213082717877957},
                                    {"x": 0.2750979483496039, "y": 0.5694983395828539},
                                ]
                            }
                        ],
                        "categories": [{"name": "OBJECT_A"}],
                        "mid": "20230407140852397-83130",
                        "type": "rectangle",
                        "isKeyFrame": False,
                    },
                ]
            }
        },
    }

    label = {"jsonResponse": json_resp}

    parsed_label = ParsedLabel(label=label, json_interface=json_interface, input_type="VIDEO")

    assert len(parsed_label.jobs["JOB_0"].frames) == 2

    frame = parsed_label.jobs["JOB_0"].frames[1]

    first_annotation = frame.annotations[0]
    assert first_annotation.category.name == "OBJECT_B"
    assert first_annotation.type == "rectangle"
    assert first_annotation.is_key_frame is True
    assert len(first_annotation.bounding_poly) == 1

    second_annotation = frame.annotations[1]
    assert second_annotation.category.name == "OBJECT_A"
    assert second_annotation.type == "rectangle"
    assert second_annotation.is_key_frame is False
    assert len(second_annotation.bounding_poly) == 1
    assert second_annotation.children["JOB_1"].categories[0].name == "IS_THE OBJECT OCCLUDED?"
    assert second_annotation.children["JOB_1"].categories[0].confidence == 100
    assert second_annotation.children["JOB_1"].is_key_frame is False

    assert parsed_label.to_dict() == label


def test_iterate_over_jobs():
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
            },
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
                    "input": "radio",
                },
                "instruction": "Pose est job",
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["pose"],
                "isChild": False,
            },
            "OBJECT_RELATION_JOB": {
                "content": {
                    "categories": {
                        "V": {
                            "children": [],
                            "color": "#5CE7B7",
                            "name": "V",
                            "startObjects": ["OBJECT_A"],
                            "endObjects": ["OBJECT_B"],
                        }
                    },
                    "input": "radio",
                },
                "instruction": "Relation job",
                "mlTask": "OBJECT_RELATION",
                "required": 0,
                "isChild": False,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "number"},
                "instruction": "Transcription number",
                "mlTask": "TRANSCRIPTION",
                "required": 0,
                "isChild": False,
            },
            "OBJECT_DETECTION_JOB_0": {
                "content": {
                    "categories": {"CAT": {"children": [], "color": "#D33BCE", "name": "Cat"}},
                    "input": "radio",
                },
                "instruction": "Semantic",
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["semantic"],
                "isChild": False,
                "models": {
                    "interactive-segmentation": {"job": "OBJECT_DETECTION_JOB_0_INTERACTIVE"}
                },
            },
            "OBJECT_DETECTION_JOB_0_INTERACTIVE": {
                "content": {
                    "categories": {"CAT": {"children": [], "color": "#D33BCE", "name": "Cat"}},
                    "input": "radio",
                },
                "instruction": "Interactive Segmentation",
                "isChild": False,
                "isModel": True,
                "isVisible": False,
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["marker"],
            },
        }
    }

    nb_jobs = 6

    json_resp = {}

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=json_resp)

    assert len(parsed_jobs) == nb_jobs

    for job_name, parsed_job_name in zip(
        sorted(json_interface["jobs"].keys()), sorted(parsed_jobs)
    ):
        assert job_name == parsed_job_name

    for i, (job_name, job_payload) in enumerate(parsed_jobs.items()):
        assert isinstance(job_payload, JobPayload)

    assert i == nb_jobs - 1  # type: ignore


def test_iterate_over_annotations():
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
                "instruction": "BBox job",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["rectangle"],
                "isChild": False,
            }
        }
    }
    normalizedVertices = [{"x": 0.43103066030618425, "y": 0.6210119016340082}] * 4
    json_resp = {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": normalizedVertices}],
                    "categories": [{"name": "A"}],
                    "mid": "25617",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "boundingPoly": [{"normalizedVertices": normalizedVertices}],
                    "categories": [{"name": "B"}],
                    "mid": "12345",
                    "type": "rectangle",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert isinstance(parsed_jobs["OBJECT_DETECTION_JOB"].annotations, AnnotationList)
    assert len(parsed_jobs["OBJECT_DETECTION_JOB"].annotations) == 2
    assert len(parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations) == 2

    for i, annotation in enumerate(parsed_jobs["OBJECT_DETECTION_JOB"].annotations):
        assert isinstance(annotation, Annotation)
        assert annotation.mid == json_resp["OBJECT_DETECTION_JOB"]["annotations"][i]["mid"]
        assert (
            annotation.category.name
            == json_resp["OBJECT_DETECTION_JOB"]["annotations"][i]["categories"][0]["name"]
        )

    for i, annotation in enumerate(parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations):
        assert isinstance(annotation, BoundingPolyAnnotation)
        assert annotation.mid == json_resp["OBJECT_DETECTION_JOB"]["annotations"][i]["mid"]
        assert (
            annotation.category.name
            == json_resp["OBJECT_DETECTION_JOB"]["annotations"][i]["categories"][0]["name"]
        )


def test_iterate_over_categories():
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
                "instruction": "Classif",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": False,
            },
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {
                        "D": {"children": ["CLASSIFICATION_JOB_0"], "color": "#472CED", "name": "D"}
                    },
                    "input": "radio",
                },
                "instruction": "BBox",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["polygon"],
                "isChild": False,
            },
            "CLASSIFICATION_JOB_0": {
                "content": {
                    "categories": {
                        "E": {"children": [], "name": "E"},
                        "F": {"children": [], "name": "F"},
                    },
                    "input": "radio",
                },
                "instruction": "sub classif",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
        }
    }

    json_resp = {
        "CLASSIFICATION_JOB": {
            "categories": [{"confidence": 100, "name": "B"}, {"confidence": 100, "name": "C"}]
        },
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB_0": {"categories": [{"confidence": 100, "name": "F"}]}
                    },
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.8601284476961973, "y": 0.4480172517038974},
                                {"x": 0.848580988145027, "y": 0.7559302912219427},
                                {"x": 0.6906799220451861, "y": 0.5418387997854648},
                            ]
                        }
                    ],
                    "categories": [{"name": "D"}],
                    "mid": "20230405140558322-57457",
                    "type": "polygon",
                }
            ]
        },
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert isinstance(parsed_jobs["CLASSIFICATION_JOB"].categories, CategoryList)
    assert len(parsed_jobs["CLASSIFICATION_JOB"].categories) == 2
    for i, category in enumerate(parsed_jobs["CLASSIFICATION_JOB"].categories):
        assert isinstance(category, Category)
        assert category.name == json_resp["CLASSIFICATION_JOB"]["categories"][i]["name"]

    assert parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations[0].category.name == "D"

    assert isinstance(
        parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations[0].children, ParsedJobs
    )
    assert len(parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations[0].children) == 1

    for category in (
        parsed_jobs["OBJECT_DETECTION_JOB"]
        .annotations[0]
        .children["CLASSIFICATION_JOB_0"]
        .categories
    ):
        assert category.name == "F"


def test_iterate_nested_transcription_bbox_get_ocr_data():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {
                            "children": ["TRANSCRIPTION_JOB"],
                            "name": "Object A",
                            "color": "#733AFB",
                        },
                        "OBJECT_B": {
                            "children": ["TRANSCRIPTION_JOB"],
                            "name": "Object B",
                            "color": "#3CD876",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "radio"},
                "instruction": "Transcription of A",
                "isChild": True,
                "mlTask": "TRANSCRIPTION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
        }
    }
    normalized_vertices = [{"x": 0.3611668381138057, "y": 0.37484025016089995}] * 4
    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {"TRANSCRIPTION_JOB": {"text": "De Bruijn"}},
                    "boundingPoly": [{"normalizedVertices": normalized_vertices}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20230405144458283-64550",
                    "type": "rectangle",
                },
                {
                    "children": {"TRANSCRIPTION_JOB": {"text": "SPECI2014"}},
                    "boundingPoly": [{"normalizedVertices": normalized_vertices}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20230405144503601-32283",
                    "type": "rectangle",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    for i, annotation in enumerate(parsed_jobs["JOB_0"].bounding_poly_annotations):
        assert (
            annotation.children["TRANSCRIPTION_JOB"].text
            == json_resp["JOB_0"]["annotations"][i]["children"]["TRANSCRIPTION_JOB"]["text"]
        )


def test_parsing_ner_in_pdf_1():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "ENTITY_A": {"children": [], "name": "Entity A", "color": "#733AFB"},
                        "ENTITY_B": {"children": [], "name": "Entity B", "color": "#3CD876"},
                    },
                    "input": "radio",
                },
                "instruction": "What entities can you identify?",
                "isChild": False,
                "tools": [],
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }
    normalizedVertices = [{"x": 0.5711857871965076, "y": 0.23031839796480386}] * 4
    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "annotations": [
                        {
                            "boundingPoly": [{"normalizedVertices": [normalizedVertices]}],
                            "pageNumberArray": [1],
                            "polys": [{"normalizedVertices": [normalizedVertices]}],
                        }
                    ],
                    "categories": [{"confidence": 100, "name": "ENTITY_A"}],
                    "content": "abcdefghijsdjfspdjfso",
                    "mid": "20230406142049158-44926",
                },
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="PDF")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    annotation_1 = parsed_jobs["JOB_0"].annotations[0]
    assert annotation_1.category.name == "ENTITY_A"
    assert annotation_1.category.confidence == 100
    assert annotation_1.content == "abcdefghijsdjfspdjfso"
    assert annotation_1.annotations[0].polys == [{"normalizedVertices": [normalizedVertices]}]
    assert annotation_1.annotations[0].bounding_poly[0].normalized_vertices == [normalizedVertices]
    assert annotation_1.annotations[0].page_number_array == [1]


def test_parsing_ner_in_pdf_2():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "ENTITY_A": {"children": [], "name": "Entity A", "color": "#733AFB"},
                        "ENTITY_B": {"children": [], "name": "Entity B", "color": "#3CD876"},
                    },
                    "input": "radio",
                },
                "instruction": "What entities can you identify?",
                "isChild": False,
                "tools": [],
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }
    normalizedVertices = [
        {"x": 0.20860370092292516, "y": 0.2975776083261186},
        {"x": 0.20860370092292516, "y": 0.5460800199831146},
        {"x": 0.7914542223597735, "y": 0.2975776083261186},
        {"x": 0.7914542223597735, "y": 0.5460800199831146},
    ]
    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "annotations": [
                        {
                            "boundingPoly": [{"normalizedVertices": [normalizedVertices]}],
                            "pageNumberArray": [1, 1, 1],
                            "polys": [
                                {
                                    "normalizedVertices": [
                                        normalizedVertices,
                                        normalizedVertices,
                                        normalizedVertices,
                                    ]
                                }
                            ],
                        }
                    ],
                    "categories": [{"confidence": 100, "name": "ENTITY_A"}],
                    "content": "While many ",
                    "mid": "20230406150551169-73300",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="PDF")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    annotation_1 = parsed_jobs["JOB_0"].annotations[0]
    assert annotation_1.category.name == "ENTITY_A"
    assert annotation_1.category.confidence == 100
    assert annotation_1.content == "While many "

    assert annotation_1.annotations[0].polys == [{"normalizedVertices": [normalizedVertices] * 3}]
    assert annotation_1.annotations[0].page_number_array == [1, 1, 1]
