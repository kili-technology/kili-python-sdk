import pytest

from kili.services.label_data_parsing.json_response import ParsedJobs


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
    parsed_jobs = ParsedJobs(
        json_response=json_resp, json_interface=json_interface, input_type="IMAGE"
    )

    assert parsed_jobs["MAIN_JOB"].category.confidence == 43
    assert parsed_jobs["MAIN_JOB"].category.name == "A"
    assert parsed_jobs["MAIN_JOB"].category.children["CLASSIFICATION_JOB"].category.name == "1"
    assert parsed_jobs["MAIN_JOB"].category.children["CLASSIFICATION_JOB"].category.confidence == 20

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
    parsed_jobs = ParsedJobs(
        json_response=json_resp, json_interface=json_interface, input_type="IMAGE"
    )

    assert parsed_jobs["MAIN_JOB"].category.confidence == 100
    assert parsed_jobs["MAIN_JOB"].category.name == "B"
    assert parsed_jobs["MAIN_JOB"].children["TRANSCRIPTION_JOB"].text == "some text"

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
    parsed_jobs = ParsedJobs(
        json_response=json_resp, json_interface=json_interface, input_type="IMAGE"
    )

    assert parsed_jobs["MAIN_JOB"].category.confidence == 100
    assert parsed_jobs["MAIN_JOB"].category.name == "C"
    assert parsed_jobs["MAIN_JOB"].children["TRANSCRIPTION_JOB_0"].text == "1337"
    assert parsed_jobs["MAIN_JOB"].children["TRANSCRIPTION_JOB_1"].text == "2013-12-13"


def test_attribute_categories_nested():
    json_response_dict = {
        "JOB_TRANSCRIPT": {"text": "sdfsdf"},
        "JOB_CLASSIF": {
            "categories": [
                {
                    "confidence": 1,
                    "name": "NAME1",
                    "children": {
                        "JOB_0": {
                            "categories": [
                                {
                                    "confidence": 2,
                                    "name": "NAME2",
                                    "children": {
                                        "JOB_1": {
                                            "categories": [
                                                {
                                                    "confidence": 3,
                                                    "name": "NAME3",
                                                    "children": {
                                                        "JOB_2": {
                                                            "categories": [
                                                                {"confidence": 4, "name": "NAME4"}
                                                            ]
                                                        },
                                                        "JOB_3": {
                                                            "categories": [
                                                                {"confidence": 5, "name": "NAME5"}
                                                            ]
                                                        },
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
        },
    }
    json_interface = {"jobs": {"JOB_TRANSCRIPT": {}, "JOB_CLASSIF": {}}}

    parsed_jobs = ParsedJobs(json_response_dict, json_interface, input_type="TEXT")

    assert parsed_jobs["JOB_TRANSCRIPT"].text == "sdfsdf"

    assert parsed_jobs["JOB_CLASSIF"].category.name == "NAME1"
    assert parsed_jobs["JOB_CLASSIF"].category.confidence == 1

    # assert parsed_jobs["JOB_CLASSIF"].children["JOB_0"].category.name == "NAME2"
    # assert parsed_jobs["JOB_CLASSIF"].children["JOB_0"].category.confidence == 2


@pytest.mark.skip(reason="Not implemented yet")
def test_attribute_categories_nested_children_wrong_place():
    json_response_dict = {
        "JOB_0": {
            "categories": [{"name": "YES_IT_IS_A_NEWS_ARTICLE", "confidence": 100}],
            "children": {"NESTED_JOB": {"categories": [{"name": "SPORTS", "confidence": 100}]}},
        }
    }
