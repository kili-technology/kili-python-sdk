from collections import defaultdict

json_interface = {
    "jobs": {
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "K": {"children": ["CLASSIFICATION_JOB"], "color": "#472CED", "name": "K"}
                },
                "input": "radio",
            },
            "instruction": "BBOX",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["rectangle"],
            "isChild": False,
        },
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "B": {"children": ["CLASSIFICATION_JOB_0"], "name": "B"},
                    "C": {"children": [], "name": "C"},
                },
                "input": "checkbox",
            },
            "instruction": "Classif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
        "CLASSIFICATION_JOB_0": {
            "content": {"categories": {"D": {"children": [], "name": "D"}}, "input": "radio"},
            "instruction": "Classif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
    }
}

bbox_1 = [
    {"x": 0.38040933358708223, "y": 0.6827307164796286},
    {"x": 0.38040933358708223, "y": 0.5827615277038205},
    {"x": 0.47514161899398205, "y": 0.5827615277038205},
    {"x": 0.47514161899398205, "y": 0.6827307164796286},
]
bbox_2 = [
    {"x": 0.22424908186164574, "y": 0.5301461651902373},
    {"x": 0.22424908186164574, "y": 0.48410772299085214},
    {"x": 0.2782760883827683, "y": 0.48410772299085214},
    {"x": 0.2782760883827683, "y": 0.5301461651902373},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "0292f264-ab07-4fcc-bf3e-a9d23d9b3623",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh888dk02v608857rae5bsy",
        "keyAnnotations": [
            {
                "id": "0292f264-ab07-4fcc-bf3e-a9d23d9b3623-3",
                "frame": 3,
                "annotationValue": {"vertices": [[bbox_1]]},
            }
        ],
        "frames": [{"start": 3, "end": 5}],
        "name": "K 1",
        "mid": "20231102143201332-74497",
        "category": "K",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "d4fd90d6-e34b-4c1e-a541-672aaf9d2588",
        "job": "CLASSIFICATION_JOB",
        "path": [["0292f264-ab07-4fcc-bf3e-a9d23d9b3623", "K"]],
        "labelId": "cloh888dk02v608857rae5bsy",
        "keyAnnotations": [
            {
                "id": "d4fd90d6-e34b-4c1e-a541-672aaf9d2588-3",
                "frame": 3,
                "annotationValue": {"categories": ["B"]},
            }
        ],
        "frames": [{"start": 3, "end": 5}],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "b8202479-0e21-4415-bb2f-b90c582b97f9",
        "job": "CLASSIFICATION_JOB_0",
        "path": [
            ["0292f264-ab07-4fcc-bf3e-a9d23d9b3623", "K"],
            ["d4fd90d6-e34b-4c1e-a541-672aaf9d2588", "B"],
        ],
        "labelId": "cloh888dk02v608857rae5bsy",
        "keyAnnotations": [
            {
                "id": "b8202479-0e21-4415-bb2f-b90c582b97f9-3",
                "frame": 3,
                "annotationValue": {"categories": ["D"]},
            }
        ],
        "frames": [{"start": 3, "end": 5}],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "769f23b1-530e-45f6-a4a2-b4e8d2c5d29a",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh888dk02v608857rae5bsy",
        "keyAnnotations": [
            {
                "id": "769f23b1-530e-45f6-a4a2-b4e8d2c5d29a-5",
                "frame": 5,
                "annotationValue": {"vertices": [[bbox_2]]},
            }
        ],
        "frames": [{"start": 5, "end": 6}],
        "name": "K 3",
        "mid": "20231102143221654-37429",
        "category": "K",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "94663f70-0833-4cf4-a0e2-c42cf60e4e9d",
        "job": "CLASSIFICATION_JOB",
        "path": [["769f23b1-530e-45f6-a4a2-b4e8d2c5d29a", "K"]],
        "labelId": "cloh888dk02v608857rae5bsy",
        "keyAnnotations": [
            {
                "id": "94663f70-0833-4cf4-a0e2-c42cf60e4e9d-5",
                "frame": 5,
                "annotationValue": {"categories": ["C"]},
            }
        ],
        "frames": [{"start": 5, "end": 6}],
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {
            "OBJECT_DETECTION_JOB": defaultdict(int, {"K": 2}),
        },
        "ANNOTATION_NAMES_JOB": {
            "20231102143201332-74497": "K 1",
            "20231102143221654-37429": "K 3",
        },
    },
    "1": {},
    "2": {},
    "3": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {
                                    "children": {
                                        "CLASSIFICATION_JOB_0": {
                                            "categories": [{"name": "D"}],
                                            "isKeyFrame": True,
                                        }
                                    },
                                    "name": "B",
                                }
                            ],
                            "isKeyFrame": True,
                        },
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "K"}],
                    "mid": "20231102143201332-74497",
                    "type": "rectangle",
                }
            ]
        }
    },
    "4": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {
                                    "children": {
                                        "CLASSIFICATION_JOB_0": {
                                            "categories": [{"name": "D"}],
                                            "isKeyFrame": False,
                                        }
                                    },
                                    "name": "B",
                                }
                            ],
                            "isKeyFrame": False,
                        },
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "K"}],
                    "mid": "20231102143201332-74497",
                    "type": "rectangle",
                }
            ]
        }
    },
    "5": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {
                                    "children": {
                                        "CLASSIFICATION_JOB_0": {
                                            "categories": [{"name": "D"}],
                                            "isKeyFrame": False,
                                        }
                                    },
                                    "name": "B",
                                }
                            ],
                            "isKeyFrame": False,
                        },
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "K"}],
                    "mid": "20231102143201332-74497",
                    "type": "rectangle",
                },
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "C"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "K"}],
                    "mid": "20231102143221654-37429",
                    "type": "rectangle",
                },
            ]
        }
    },
    "6": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "C"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "K"}],
                    "mid": "20231102143221654-37429",
                    "type": "rectangle",
                }
            ]
        }
    },
}
