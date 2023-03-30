import json

from kili.services.label_data_parsing.category import Category, CategoryList
from kili.utils.labels import parse_labels


def test_parse_labels_classification():
    labels = [
        {
            "author": {
                "email": "kili@kili-technology.com",
                "id": "123",
            },
            "id": "456",
            "jsonResponse": {"REQUIRED_JOB": {"categories": [{"confidence": 100, "name": "A"}]}},
            "labelType": "DEFAULT",
            "secondsToLabel": 9,
        },
        {
            "author": {
                "email": "kili@kili-technology.com",
                "id": "123",
            },
            "id": "789",
            "jsonResponse": {
                "REQUIRED_JOB": {"categories": [{"confidence": 90, "name": "B"}]},
                "NON_REQUIRED_JOB": {"categories": [{"confidence": 80, "name": "C"}]},
            },
            "labelType": "DEFAULT",
            "secondsToLabel": 3,
        },
    ]

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
                "instruction": "Required",
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
                "instruction": "Non required",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            },
        }
    }
    labels = parse_labels(labels, json_interface=json_interface)

    assert labels[0].jobs["REQUIRED_JOB"].category.name == "A"
    assert labels[0].jobs["REQUIRED_JOB"].category.confidence == 100

    assert labels[1].jobs["REQUIRED_JOB"].categories[0].name == "B"
    assert labels[1].jobs["NON_REQUIRED_JOB"].categories[0].name == "C"


def test_parse_labels_classification_to_dict():
    """Test that checks that parsing the categories to CategoryList and Category
    objects still allows to convert to dict and json."""
    labels = [
        {
            "author": {
                "email": "kili@kili-technology.com",
                "id": "123",
            },
            "id": "456",
            "jsonResponse": {"REQUIRED_JOB": {"categories": [{"confidence": 100, "name": "A"}]}},
            "labelType": "DEFAULT",
            "secondsToLabel": 9,
        }
    ]

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
                "instruction": "Required",
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
                "instruction": "Non required",
                "mlTask": "CLASSIFICATION",
                "required": 0,
                "isChild": False,
            },
        }
    }
    parsed_labels = parse_labels(labels, json_interface=json_interface)

    # we query the category name and checks that the label has been converted to
    # CategoryList and Category objects
    # they inherit from Dict and List so they should be serializable
    assert parsed_labels[0].jobs["REQUIRED_JOB"].category.name == "A"
    assert isinstance(parsed_labels[0].jobs["REQUIRED_JOB"].category, Category)
    assert isinstance(parsed_labels[0].jobs["REQUIRED_JOB"].categories, CategoryList)

    # test that json.dumps works.
    # It would fail if the label is not serializable anymore after parsing.
    label_0_modified_as_str = json.dumps(parsed_labels[0])

    label_0_modifed = json.loads(label_0_modified_as_str)

    assert label_0_modifed == labels[0]
