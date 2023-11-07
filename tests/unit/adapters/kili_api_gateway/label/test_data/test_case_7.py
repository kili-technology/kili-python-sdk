json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB_": {
            "content": {
                "categories": {
                    "A": {"children": ["CLASSIFICATION_JOB_0_"], "name": "A"},
                    "B": {"children": [], "name": "B"},
                },
                "input": "singleDropdown",
            },
            "instruction": "Classif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
        },
        "CLASSIFICATION_JOB_0_": {
            "content": {"categories": {"C": {"children": [], "name": "C"}}, "input": "checkbox"},
            "instruction": "SubClassif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
    }
}

annotations = [
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "89fae1e5-c33f-4280-8cb7-73c488e2ece1",
        "job": "CLASSIFICATION_JOB_0_",
        "path": [["69144fde-557c-402e-9c57-c515dd1a6c96", "A"]],
        "labelId": "cloh8vkke038t0885egwy2fky",
        "frames": [{"start": 5, "end": 7}],
        "keyAnnotations": [
            {
                "id": "89fae1e5-c33f-4280-8cb7-73c488e2ece1-5",
                "frame": 5,
                "isPrediction": False,
                "annotationValue": {"categories": ["C"]},
            }
        ],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "69144fde-557c-402e-9c57-c515dd1a6c96",
        "job": "CLASSIFICATION_JOB_",
        "path": [],
        "labelId": "cloh8vkke038t0885egwy2fky",
        "frames": [{"start": 5, "end": 14}],
        "keyAnnotations": [
            {
                "id": "69144fde-557c-402e-9c57-c515dd1a6c96-5",
                "frame": 5,
                "isPrediction": False,
                "annotationValue": {"categories": ["A"]},
            },
            {
                "id": "69144fde-557c-402e-9c57-c515dd1a6c96-10",
                "frame": 10,
                "isPrediction": False,
                "annotationValue": {"categories": ["B"]},
            },
        ],
    },
]

expected_json_resp = {
    "5": {
        "CLASSIFICATION_JOB_": {
            "categories": [
                {
                    "name": "A",
                    "children": {
                        "CLASSIFICATION_JOB_0_": {
                            "categories": [{"name": "C"}],
                            "isKeyFrame": True,
                        }
                    },
                }
            ],
            "isKeyFrame": True,
        }
    },
    "6": {
        "CLASSIFICATION_JOB_": {
            "categories": [
                {
                    "name": "A",
                    "children": {
                        "CLASSIFICATION_JOB_0_": {
                            "categories": [{"name": "C"}],
                            "isKeyFrame": False,
                        }
                    },
                }
            ],
            "isKeyFrame": False,
        }
    },
    "7": {
        "CLASSIFICATION_JOB_": {
            "categories": [
                {
                    "name": "A",
                    "children": {
                        "CLASSIFICATION_JOB_0_": {
                            "categories": [{"name": "C"}],
                            "isKeyFrame": False,
                        }
                    },
                }
            ],
            "isKeyFrame": False,
        }
    },
    "8": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "A"}],
            "isKeyFrame": False,
        }
    },
    "9": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "A"}],
            "isKeyFrame": False,
        }
    },
    "10": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "B"}],
            "isKeyFrame": True,
        }
    },
    "11": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "B"}],
            "isKeyFrame": False,
        }
    },
    "12": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "B"}],
            "isKeyFrame": False,
        }
    },
    "13": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "B"}],
            "isKeyFrame": False,
        }
    },
    "14": {
        "CLASSIFICATION_JOB_": {
            "categories": [{"name": "B"}],
            "isKeyFrame": False,
        }
    },
}
