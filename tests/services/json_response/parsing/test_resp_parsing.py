from kili.services.json_response.json_response import ParsedJobs


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


def test_attribute_categories():
    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "A"}]}}
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
    categories = parsed_jobs["JOB_0"].categories

    assert parsed_jobs["JOB_0"].category.name == categories[0].name == "A"
    assert parsed_jobs["JOB_0"].category.confidence == categories[0].confidence == 100


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
