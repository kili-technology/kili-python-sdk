import pytest

from kili.services.json_response.json_response import ParsedJobs


@pytest.mark.skip("Not implemented yet")
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

    parsed_jobs = ParsedJobs(json_response_dict, json_interface)

    assert parsed_jobs["JOB_TRANSCRIPT"].text == "sdfsdf"

    assert parsed_jobs["JOB_CLASSIF"].category.name == "NAME1"
    assert parsed_jobs["JOB_CLASSIF"].category.confidence == 1

    # assert parsed_jobs["JOB_CLASSIF"].children["JOB_0"].category.name == "NAME2"
    # assert parsed_jobs["JOB_CLASSIF"].children["JOB_0"].category.confidence == 2


@pytest.mark.skip("Not implemented yet")
def test_attribute_categories_nested_children_wrong_place():
    json_response_dict = {
        "JOB_0": {
            "categories": [{"name": "YES_IT_IS_A_NEWS_ARTICLE", "confidence": 100}],
            "children": {"NESTED_JOB": {"categories": [{"name": "SPORTS", "confidence": 100}]}},
        }
    }
