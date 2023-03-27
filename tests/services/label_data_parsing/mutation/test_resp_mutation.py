from kili.services.label_data_parsing.json_response import ParsedJobs


def test_mutate_transcription_label():
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1}}}

    json_response_dict = {"JOB_0": {"text": "This is a transcription job"}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_0"].text == "This is a transcription job"

    parsed_jobs["JOB_0"].text = "This is a transcription job that has been mutated"
    assert parsed_jobs["JOB_0"].text == "This is a transcription job that has been mutated"


def test_mutate_transcription_label_non_required():
    json_interface = {"jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 0}}}

    json_response_dict = {}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    parsed_jobs["JOB_0"].text = "This is a transcription job"
    assert parsed_jobs["JOB_0"].text == "This is a transcription job"


def test_mutate_category():
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
            }
        }
    }

    json_response_dict = {"JOB_0": {"categories": [{"confidence": 100, "name": "C"}]}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

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
            }
        }
    }

    json_response_dict = {}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

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

    parsed_jobs = ParsedJobs(json_resp_dict, json_interface)

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

    parsed_jobs["JOB_0"].entity_annotations[0].categories[0].name = "PERSON"
    parsed_jobs["JOB_0"].entity_annotations[0].categories[0].confidence = 98
    parsed_jobs["JOB_0"].entity_annotations[0].begin_offset = 42
    parsed_jobs["JOB_0"].entity_annotations[0].content = "abcdef"
    parsed_jobs["JOB_0"].entity_annotations[0].mid = "new mid"

    assert parsed_jobs["JOB_0"].entity_annotations[0].category.name == "PERSON"
    assert parsed_jobs["JOB_0"].entity_annotations[0].category.confidence == 98
    assert parsed_jobs["JOB_0"].entity_annotations[0].begin_offset == 42
    assert parsed_jobs["JOB_0"].entity_annotations[0].content == "abcdef"
    assert parsed_jobs["JOB_0"].entity_annotations[0].mid == "new mid"


def test_mutate_ner_project_annotations():
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

    parsed_jobs["JOB_0"].annotations[0].categories[0].name = "PERSON"
    parsed_jobs["JOB_0"].annotations[0].categories[0].confidence = 98
    parsed_jobs["JOB_0"].annotations[0].begin_offset = 42
    parsed_jobs["JOB_0"].annotations[0].content = "abcdef"
    parsed_jobs["JOB_0"].annotations[0].mid = "new mid"

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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

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

    parsed_jobs = ParsedJobs(json_resp, json_interface)

    parsed_jobs["NON_REQUIRED_JOB"].add_category("C", 100)

    assert parsed_jobs["NON_REQUIRED_JOB"].categories[0].name == "C"
