from kili.services.label_data_parsing.bounding_poly import BoundingPoly
from kili.services.label_data_parsing.json_response import ParsedJobs


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

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)
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

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)
    categories = parsed_jobs["JOB_0"].categories

    assert categories[0].confidence == 42
    assert categories[0].name == "A"
    assert categories[1].confidence == 100
    assert categories[1].name == "B"


def test_attribute_text():
    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

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
                "content": {
                    "categories": {"ORG": {}, "PERSON": {}},
                    "input": "radio",
                },
            }
        }
    }

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

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
                "content": {"categories": {"A": {}, "B": {}}, "input": "radio"},
            }
        }
    }

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

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
            }
        }
    }

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}
    parsed_jobs = ParsedJobs(json_resp, json_interface)
    category = parsed_jobs["CLASSIFICATION_JOB"].category
    assert category.name == "B"
    assert category.confidence == 100

    json_resp = {}  # asset annotated but no category chosen
    parsed_jobs = ParsedJobs(json_resp, json_interface)
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
            }
        }
    }

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}
    parsed_jobs = ParsedJobs(json_resp, json_interface)

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
            }
        }
    }

    json_resp = {"CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "B"}]}}
    parsed_jobs = ParsedJobs(json_resp, json_interface)
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100

    json_resp = {
        "CLASSIFICATION_JOB": {
            "categories": [{"confidence": 100, "name": "B"}, {"confidence": 52, "name": "A"}]
        }
    }
    parsed_jobs = ParsedJobs(json_resp, json_interface)
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].name == "B"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[0].confidence == 100
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].name == "A"
    assert parsed_jobs["CLASSIFICATION_JOB"].categories[1].confidence == 52

    json_resp = {}  # asset annotated but no classes chosen
    parsed_jobs = ParsedJobs(json_resp, json_interface)
    assert parsed_jobs["CLASSIFICATION_JOB"].categories == []


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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

    bb_annotations = parsed_jobs["OBJECT_DETECTION_JOB"].bounding_poly_annotations

    assert bb_annotations[0].category.name == bb_annotations[0].categories[0].name == "A"
    assert bb_annotations[1].category.name == bb_annotations[1].categories[0].name == "B"
    assert bb_annotations[2].category.name == bb_annotations[2].categories[0].name == "C"

    assert bb_annotations[0].type == "rectangle"
    assert bb_annotations[1].type == "rectangle"
    assert bb_annotations[2].type == "rectangle"

    assert bb_annotations[0].mid == "20230323105350648-87611"

    my_parsed_job = parsed_jobs["OBJECT_DETECTION_JOB"]
    assert isinstance(my_parsed_job.bounding_poly_annotations[0].bounding_poly, BoundingPoly)
    assert isinstance(my_parsed_job.annotations[0].bounding_poly, BoundingPoly)

    assert my_parsed_job.bounding_poly_annotations[0].bounding_poly.normalized_vertices == vertices


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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

    job = parsed_jobs["OBJECT_DETECTION_JOB"]

    assert job.annotations[0].categories[0].name == "A"

    assert job.annotations[1].type == "marker"

    assert job.annotations[1].point == point
