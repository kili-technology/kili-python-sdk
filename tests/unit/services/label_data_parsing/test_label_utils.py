import json
from typing import List

from typing_extensions import assert_type

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.label import LabelClientMethods
from kili.services.label_data_parsing.annotation import Annotation, AnnotationList
from kili.services.label_data_parsing.category import Category, CategoryList
from kili.utils.labels.parsing import ParsedLabel, parse_labels


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
    labels = parse_labels(labels, json_interface=json_interface, input_type="IMAGE")

    assert labels[0].jobs["REQUIRED_JOB"].category.name == "A"
    assert labels[0].jobs["REQUIRED_JOB"].category.confidence == 100

    assert labels[1].jobs["REQUIRED_JOB"].categories[0].name == "B"
    assert labels[1].jobs["NON_REQUIRED_JOB"].categories[0].name == "C"


def test_parse_labels_classification_to_dict():
    """test_parse_labels_classification_to_dict.

    Test that checks that parsing the categories to CategoryList and Category
    objects still allows to convert to dict and json.
    """
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
        }
    }
    parsed_labels = parse_labels(labels, json_interface=json_interface, input_type="IMAGE")

    # we check that the label has been converted to CategoryList and Category objects
    assert isinstance(parsed_labels[0].jobs["REQUIRED_JOB"].category, Category)
    assert isinstance(parsed_labels[0].jobs["REQUIRED_JOB"].categories, CategoryList)

    # make some modifications to the label...
    parsed_labels[0].jobs["REQUIRED_JOB"].category.name = "B"
    parsed_labels[0].jobs["REQUIRED_JOB"].category.confidence = 90

    # test that json.dumps works.
    # It would fail if the label is not serializable anymore after parsing.
    label_0_modified_as_str = json.dumps(parsed_labels[0].to_dict())

    label_0_modifed = json.loads(label_0_modified_as_str)

    assert label_0_modifed == {
        "author": {
            "email": "kili@kili-technology.com",
            "id": "123",
        },
        "id": "456",
        "jsonResponse": {"REQUIRED_JOB": {"categories": [{"confidence": 90, "name": "B"}]}},
        "labelType": "DEFAULT",
        "secondsToLabel": 9,
    }


def test_parse_labels_classification_to_dict_classif_with_bbox():
    """test_parse_labels_classification_to_dict_classif_with_bbox.

    Test that checks that parsing the categories to custom objects (CategoryList, Category, etc.)
    still allows to convert to dict and json.
    """
    vertices = [
        {"x": 0.5141441957015471, "y": 0.6164292619007603},
        {"x": 0.5141441957015471, "y": 0.367821056372058},
        {"x": 0.7138743970392409, "y": 0.367821056372058},
        {"x": 0.7138743970392409, "y": 0.6164292619007603},
    ]
    label_0 = {
        "author": {
            "email": "kili@kili-technology.com",
            "id": "123456",
        },
        "id": "clftfp95d003d0ju64lxohiyl",
        "jsonResponse": {},
        "labelType": "DEFAULT",
        "secondsToLabel": 1,
    }
    label_1 = {
        "author": {
            "email": "kili@kili-technology.com",
            "id": "123456",
        },
        "id": "clftp19to01ia0jrme8vu4xcy",
        "jsonResponse": {
            "JOB_0": {
                "annotations": [
                    {
                        "children": {},
                        "boundingPoly": [{"normalizedVertices": vertices}],
                        "categories": [{"name": "A"}],
                        "mid": "20230329145907681-18624",
                        "type": "rectangle",
                    }
                ]
            }
        },
        "labelType": "DEFAULT",
        "secondsToLabel": 3,
    }
    label_2 = {
        "author": {
            "email": "kili@kili-technology.com",
            "id": "123456",
        },
        "id": "clftp19to01ia0jrme8vu4xcy",
        "jsonResponse": {
            "JOB_0": {
                "annotations": [
                    {
                        "children": {},
                        "boundingPoly": [{"normalizedVertices": vertices}],
                        "categories": [{"name": "A"}],
                        "mid": "20230329145907681-18624",
                        "type": "rectangle",
                    },
                    {
                        "children": {},
                        "boundingPoly": [{"normalizedVertices": vertices}],
                        "categories": [{"name": "B"}],
                        "mid": "20230329145907681-18624",
                        "type": "rectangle",
                    },
                ]
            }
        },
        "labelType": "DEFAULT",
        "secondsToLabel": 3,
    }

    labels = [label_0, label_1, label_2]

    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "A": {"children": [], "color": "#472CED", "name": "A"},
                        "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                    },
                    "input": "radio",
                },
                "instruction": "Class",
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["rectangle"],
                "isChild": False,
            }
        }
    }
    parsed_labels = parse_labels(labels, json_interface=json_interface, input_type="IMAGE")

    for label in parsed_labels:
        assert isinstance(label.jobs["JOB_0"].annotations, AnnotationList)
        if len(label.jobs["JOB_0"].annotations) > 0:
            assert isinstance(label.jobs["JOB_0"].annotations[0], Annotation)

    # test that json.dumps works.
    # It would fail if the label is not serializable anymore after parsing.
    labels_modified_as_str = [json.dumps(label.to_dict()) for label in parsed_labels]

    labels_modified = [
        json.loads(label_modified_as_str) for label_modified_as_str in labels_modified_as_str
    ]

    for original_label, parsed_label in zip(labels, labels_modified):
        assert original_label == parsed_label


def test_integration_of_label_parsing_in_kili_labels(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": {
            "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1, "isChild": False}}
        },
        "inputType": "TEXT",
    }
    kili_api_gateway.list_labels.return_value = (
        label for label in [{"jsonResponse": {"JOB_0": {"text": "some text abc"}}}]
    )

    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    labels = kili.labels(project_id="project_id", output_format="parsed_label")

    assert_type(labels, List[ParsedLabel])

    assert isinstance(labels, List)
    assert all(isinstance(labl, ParsedLabel) for labl in labels)  # pylint: disable=not-an-iterable
    assert len(labels) == 1
    assert labels[0].jobs["JOB_0"].text == "some text abc"  # pylint: disable=unsubscriptable-object
