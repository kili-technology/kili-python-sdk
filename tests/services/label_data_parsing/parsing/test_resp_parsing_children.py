from copy import deepcopy

import pytest

from kili.services.label_data_parsing.json_response import ParsedJobs
from kili.services.label_data_parsing.types import Project


def test_multiple_jobs_with_children_jobs():
    json_interface = {
        "jobs": {
            "MAIN_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": ["CLASSIFICATION_JOB"], "name": "A"},
                        "B": {"children": ["TRANSCRIPTION_JOB"], "name": "B"},
                        "C": {
                            "children": ["TRANSCRIPTION_JOB_0", "TRANSCRIPTION_JOB_1"],
                            "name": "C",
                        },
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {
                        "1": {"children": [], "name": "1"},
                        "2": {"children": [], "name": "2"},
                    },
                    "input": "radio",
                },
                "instruction": "Sub category A",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "textField"},
                "instruction": "Transcription",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": True,
            },
            "TRANSCRIPTION_JOB_0": {
                "content": {"input": "number"},
                "instruction": "Number",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": True,
            },
            "TRANSCRIPTION_JOB_1": {
                "content": {"input": "date"},
                "instruction": "Date",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": True,
            },
        }
    }
    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore

    json_resp = {
        "MAIN_JOB": {
            "categories": [
                {
                    "confidence": 43,
                    "name": "A",
                    "children": {
                        "CLASSIFICATION_JOB": {"categories": [{"confidence": 20, "name": "1"}]}
                    },
                }
            ]
        }
    }
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["MAIN_JOB"].category.confidence == 43
    assert parsed_jobs["MAIN_JOB"].category.name == "A"
    assert parsed_jobs["MAIN_JOB"].category.children["CLASSIFICATION_JOB"].category.name == "1"
    assert parsed_jobs["MAIN_JOB"].category.children["CLASSIFICATION_JOB"].category.confidence == 20
    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp

    json_resp = {
        "MAIN_JOB": {
            "categories": [
                {
                    "confidence": 100,
                    "name": "B",
                    "children": {"TRANSCRIPTION_JOB": {"text": "some text"}},
                }
            ]
        }
    }
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["MAIN_JOB"].category.confidence == 100
    assert parsed_jobs["MAIN_JOB"].category.name == "B"
    assert parsed_jobs["MAIN_JOB"].category.children["TRANSCRIPTION_JOB"].text == "some text"
    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp

    json_resp = {
        "MAIN_JOB": {
            "categories": [
                {
                    "confidence": 100,
                    "name": "C",
                    "children": {
                        "TRANSCRIPTION_JOB_0": {"text": "1337"},
                        "TRANSCRIPTION_JOB_1": {"text": "2013-12-13"},
                    },
                }
            ]
        }
    }
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["MAIN_JOB"].category.confidence == 100
    assert parsed_jobs["MAIN_JOB"].category.name == "C"
    assert parsed_jobs["MAIN_JOB"].category.children["TRANSCRIPTION_JOB_0"].text == "1337"
    assert parsed_jobs["MAIN_JOB"].category.children["TRANSCRIPTION_JOB_1"].text == "2013-12-13"
    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_attribute_categories_nested():
    json_resp = {
        "JOB_0": {
            "categories": [
                {
                    "confidence": 1,
                    "name": "A",
                    "children": {
                        "JOB_1": {
                            "categories": [
                                {
                                    "confidence": 2,
                                    "name": "B",
                                    "children": {
                                        "JOB_2": {
                                            "categories": [
                                                {
                                                    "confidence": 3,
                                                    "name": "C",
                                                    "children": {
                                                        "JOB_3": {
                                                            "categories": [
                                                                {"confidence": 4, "name": "D"}
                                                            ]
                                                        }
                                                    },
                                                }
                                            ]
                                        }
                                    },
                                }
                            ]
                        }
                    },
                }
            ]
        }
    }
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {"A": {"children": ["JOB_1"], "name": "A"}},
                    "input": "radio",
                },
                "instruction": "Job1",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "JOB_1": {
                "content": {
                    "categories": {"B": {"children": ["JOB_2"], "name": "B"}},
                    "input": "radio",
                },
                "instruction": "Job2",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
            "JOB_2": {
                "content": {
                    "categories": {"C": {"children": ["JOB_3"], "name": "C"}},
                    "input": "radio",
                },
                "instruction": "Job3",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
            "JOB_3": {
                "content": {"categories": {"D": {"children": [], "name": "D"}}, "input": "radio"},
                "instruction": "Job4",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
        }
    }
    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore

    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["JOB_0"].category.confidence == 1
    assert parsed_jobs["JOB_0"].category.children["JOB_1"].category.confidence == 2
    assert (
        parsed_jobs["JOB_0"]
        .category.children["JOB_1"]
        .category.children["JOB_2"]
        .category.confidence
        == 3
    )
    assert (
        parsed_jobs["JOB_0"]
        .category.children["JOB_1"]
        .category.children["JOB_2"]
        .category.children["JOB_3"]
        .category.confidence
        == 4
    )

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_attribute_categories_nested_children_wrong_place():
    json_resp = {
        "JOB_0": {
            "categories": [{"name": "YES_IT_IS_A_NEWS_ARTICLE", "confidence": 42}],
            "children": {"NESTED_JOB": {"categories": [{"name": "SPORTS", "confidence": 100}]}},
        }
    }

    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "YES_IT_IS_A_NEWS_ARTICLE": {
                            "children": ["NESTED_JOB"],
                            "name": "YES_IT_IS_A_NEWS_ARTICLE",
                        }
                    },
                    "input": "radio",
                },
                "instruction": "Job1",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "NESTED_JOB": {
                "content": {
                    "categories": {"SPORTS": {"children": [], "name": "SPORTS"}},
                    "input": "radio",
                },
                "instruction": "Job2",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore

    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["JOB_0"].category.confidence == 42
    assert parsed_jobs["JOB_0"].category.name == "YES_IT_IS_A_NEWS_ARTICLE"
    assert parsed_jobs["JOB_0"].children["NESTED_JOB"].category.confidence == 100
    assert parsed_jobs["JOB_0"].children["NESTED_JOB"].category.name == "SPORTS"

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_parsing_bbox_job_with_classif_subjob_and_transcription_subjob():
    json_interface = {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {
                        "A": {
                            "children": ["CLASSIFICATION_JOB", "TRANSCRIPTION_JOB"],
                            "color": "#472CED",
                            "name": "A",
                        }
                    },
                    "input": "radio",
                },
                "instruction": "BBox",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["rectangle"],
                "isChild": False,
            },
            "CLASSIFICATION_JOB": {
                "content": {"categories": {"B": {"children": [], "name": "B"}}, "input": "radio"},
                "instruction": "Classif task",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "textField"},
                "instruction": "Transcription task",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": True,
            },
        }
    }

    json_resp = {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]},
                        "TRANSCRIPTION_JOB": {"text": "some text"},
                    },
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.5734189651307983, "y": 0.33436362565639133},
                                {"x": 0.5734189651307983, "y": 0.10309483010170684},
                                {"x": 0.7995650963228321, "y": 0.10309483010170684},
                                {"x": 0.7995650963228321, "y": 0.33436362565639133},
                            ]
                        }
                    ],
                    "categories": [{"name": "A"}],
                    "mid": "20230404094129314-32394",
                    "type": "rectangle",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].category.name == "A"
    assert parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].mid == "20230404094129314-32394"

    assert (
        parsed_jobs["OBJECT_DETECTION_JOB"]
        .annotations[0]
        .children["CLASSIFICATION_JOB"]
        .category.name
        == "B"
    )

    assert (
        parsed_jobs["OBJECT_DETECTION_JOB"].annotations[0].children["TRANSCRIPTION_JOB"].text
        == "some text"
    )

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_bbox_with_nested_classif():
    json_interface = {
        "jobs": {
            "JOB": {
                "content": {
                    "categories": {
                        "FERRARI": {
                            "children": ["CLASSIFICATION_JOB"],
                            "color": "#472CED",
                            "name": "FERRARI",
                        }
                    },
                    "input": "radio",
                },
                "instruction": "BBox",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["rectangle"],
                "isChild": False,
            },
            "CLASSIFICATION_JOB": {
                "content": {
                    "categories": {"GREY": {"children": [], "name": "GREY"}},
                    "input": "radio",
                },
                "instruction": "Classif task",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
        }
    }

    json_resp = {
        "JOB": {
            "annotations": [
                {
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.09, "y": 0.84},
                                {"x": 0.09, "y": 0.36},
                                {"x": 0.92, "y": 0.36},
                                {"x": 0.92, "y": 0.84},
                            ]
                        }
                    ],
                    "categories": [{"name": "FERRARI", "confidence": 100}],
                    "mid": "unique-ferrari",
                    "type": "rectangle",
                    "children": {
                        "CLASSIFICATION_JOB": {"categories": [{"name": "GREY", "confidence": 42}]}
                    },
                }
            ]
        }
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="IMAGE")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["JOB"].annotations[0].category.name == "FERRARI"
    assert parsed_jobs["JOB"].annotations[0].mid == "unique-ferrari"

    assert (
        parsed_jobs["JOB"].bounding_poly_annotations[0].children["CLASSIFICATION_JOB"].category.name
        == "GREY"
    )
    assert (
        parsed_jobs["JOB"]
        .bounding_poly_annotations[0]
        .children["CLASSIFICATION_JOB"]
        .category.confidence
        == 42
    )

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_ner_text_project_with_classif_children_job():
    job_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "INTERJECTION": {
                            "children": ["CLASSIFICATION_JOB"],
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
                "isVisible": True,
                "required": 1,
            },
            "CLASSIFICATION_JOB": {
                "content": {"categories": {"A": {"children": [], "name": "A"}}, "input": "radio"},
                "instruction": "Classif",
                "mlTask": "CLASSIFICATION",
                "required": 1,
                "isChild": True,
            },
        }
    }

    json_resp = {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "A"}]}
                    },
                    "beginId": "main/[0]",
                    "beginOffset": 497,
                    "categories": [{"name": "INTERJECTION"}],
                    "content": "mpor. Cras vestib",
                    "endId": "main/[0]",
                    "endOffset": 514,
                    "mid": "20230404162231697-76830",
                }
            ]
        }
    }

    project_info = Project(jsonInterface=job_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["JOB_0"].entity_annotations[0].category.name == "INTERJECTION"
    assert parsed_jobs["JOB_0"].entity_annotations[0].begin_offset == 497
    assert parsed_jobs["JOB_0"].entity_annotations[0].end_offset == 514

    assert (
        parsed_jobs["JOB_0"].entity_annotations[0].children["CLASSIFICATION_JOB"].category.name
        == "A"
    )

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp


def test_relation_job():
    json_interface = {
        "jobs": {
            "NAMED_ENTITIES_RELATION_JOB": {
                "content": {
                    "categories": {
                        "RELATION": {
                            "children": ["TRANSCRIPTION_JOB"],
                            "color": "#472CED",
                            "name": "Relation",
                            "startEntities": ["ANY"],
                            "endEntities": ["ANY"],
                        }
                    },
                    "input": "radio",
                },
                "instruction": "Thing",
                "mlTask": "NAMED_ENTITIES_RELATION",
                "required": 1,
                "isChild": False,
            },
            "TRANSCRIPTION_JOB": {
                "content": {"input": "textField"},
                "instruction": "Text",
                "mlTask": "TRANSCRIPTION",
                "required": 1,
                "isChild": True,
            },
            "NAMED_ENTITIES_RECOGNITION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "color": "#5CE7B7", "name": "A"},
                        "B": {"children": [], "name": "B", "color": "#D33BCE"},
                    },
                    "input": "radio",
                },
                "instruction": "Class",
                "mlTask": "NAMED_ENTITIES_RECOGNITION",
                "required": 1,
                "isChild": False,
            },
        }
    }

    json_resp = {
        "NAMED_ENTITIES_RECOGNITION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "beginId": "main/[0]",
                    "beginOffset": 743,
                    "categories": [{"name": "A"}],
                    "content": ". Mauri",
                    "endId": "main/[0]",
                    "endOffset": 750,
                    "mid": "20230404163931564-84302",
                },
                {
                    "children": {},
                    "beginId": "main/[0]",
                    "beginOffset": 477,
                    "categories": [{"name": "B"}],
                    "content": (
                        "t libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas"
                        " leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue"
                        " blandit sodales. Vestibulum ante ipsum primis in faucibus"
                    ),
                    "endId": "main/[0]",
                    "endOffset": 683,
                    "mid": "20230404163933009-81517",
                },
            ]
        },
        "NAMED_ENTITIES_RELATION_JOB": {
            "annotations": [
                {
                    "children": {"TRANSCRIPTION_JOB": {"text": "truc"}},
                    "categories": [{"name": "RELATION"}],
                    "endEntities": [{"mid": "20230404163933009-81517"}],
                    "mid": "20230404163934799-28300",
                    "startEntities": [{"mid": "20230404163931564-84302"}],
                }
            ]
        },
    }

    project_info = Project(jsonInterface=json_interface["jobs"], inputType="TEXT")  # type: ignore
    parsed_jobs = ParsedJobs(project_info=project_info, json_response=deepcopy(json_resp))

    assert parsed_jobs["NAMED_ENTITIES_RECOGNITION_JOB"].entity_annotations[0].begin_offset == 743
    assert parsed_jobs["NAMED_ENTITIES_RECOGNITION_JOB"].entity_annotations[0].content == ". Mauri"

    assert (
        parsed_jobs["NAMED_ENTITIES_RELATION_JOB"].annotations[0].children["TRANSCRIPTION_JOB"].text
        == "truc"
    )

    parsed_jobs_as_dict = parsed_jobs.to_dict()
    assert parsed_jobs_as_dict == json_resp
