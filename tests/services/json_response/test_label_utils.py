from kili.utils.labels import parse_labels


def test_parse_labels():
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
