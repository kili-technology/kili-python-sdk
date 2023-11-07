json_interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": ["JOB_1"], "name": "Train", "color": "#733AFB"}
                },
                "input": "radio",
            },
            "instruction": "Track objects A and B",
            "isChild": False,
            "tools": ["rectangle"],
            "mlTask": "OBJECT_DETECTION",
            "models": {"tracking": {}},
            "isVisible": True,
            "required": 0,
        },
        "JOB_1": {
            "content": {
                "categories": {
                    "IS_THE OBJECT OCCLUDED?": {"children": [], "name": "Is the object occluded?"}
                },
                "input": "checkbox",
            },
            "instruction": "",
            "isChild": True,
            "mlTask": "CLASSIFICATION",
            "models": {},
            "isVisible": True,
            "required": 0,
        },
    }
}

bbox_1 = [
    {"x": 0.1, "y": 0.7},
    {"x": 0.1, "y": 0.5},
    {"x": 0.3, "y": 0.5},
    {"x": 0.3, "y": 0.7},
]

bbox_2 = [
    {"x": 0.4, "y": 0.7},
    {"x": 0.4, "y": 0.5},
    {"x": 0.6, "y": 0.5},
    {"x": 0.6, "y": 0.7},
]

bbox_3 = [
    {"x": 0.4, "y": 0.3},
    {"x": 0.4, "y": 0.1},
    {"x": 0.6, "y": 0.1},
    {"x": 0.6, "y": 0.3},
]

bbox_4 = [
    {"x": 0.4, "y": 0.3},
    {"x": 0.4, "y": 0.1},
    {"x": 0.6, "y": 0.1},
    {"x": 0.6, "y": 0.3},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "277417a2-c99d-4ae3-aff1-472094315c56",
        "job": "JOB_0",
        "path": [],
        "labelId": "cloibot0x0329083fg7jxfea9",
        "keyAnnotations": [
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_1]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-3",
                "frame": 3,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_2]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-9",
                "frame": 9,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_4]]},
            },
            {
                "id": "277417a2-c99d-4ae3-aff1-472094315c56-7",
                "frame": 7,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_3]]},
            },
        ],
        "frames": [{"start": 0, "end": 9}],
        "name": "Train 1",
        "mid": "20231103085506560-87322",
        "category": "OBJECT_A",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "946a8b83-cac3-4400-af04-0ec0895a3e75",
        "job": "JOB_1",
        "path": [["277417a2-c99d-4ae3-aff1-472094315c56", "OBJECT_A"]],
        "labelId": "cloibot0x0329083fg7jxfea9",
        "keyAnnotations": [
            {
                "id": "946a8b83-cac3-4400-af04-0ec0895a3e75-7",
                "frame": 7,
                "isPrediction": False,
                "annotationValue": {"categories": ["IS_THE OBJECT OCCLUDED?"]},
            }
        ],
        "frames": [{"start": 7, "end": 8}],
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {
            "JOB_0": {"OBJECT_A": 1},
        },
        "ANNOTATION_NAMES_JOB": {
            "20231103085506560-87322": "Train 1",
        },
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        },
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.2, "y": 0.7},
                                {"x": 0.2, "y": 0.5},
                                {"x": 0.4, "y": 0.5},
                                {"x": 0.4, "y": 0.7},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        }
    },
    "2": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.3, "y": 0.7},
                                {"x": 0.3, "y": 0.5},
                                {"x": 0.5, "y": 0.5},
                                {"x": 0.5, "y": 0.7},
                            ]
                        }
                    ],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                }
            ]
        }
    },
    "3": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                }
            ]
        }
    },
    "4": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.4, "y": 0.6},
                                {"x": 0.4, "y": 0.4},
                                {"x": 0.6, "y": 0.4},
                                {"x": 0.6, "y": 0.6},
                            ]
                        }
                    ],
                }
            ]
        }
    },
    "5": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.4, "y": 0.5},
                                {"x": 0.4, "y": 0.3},
                                {"x": 0.6, "y": 0.3},
                                {"x": 0.6, "y": 0.5},
                            ]
                        }
                    ],
                }
            ]
        }
    },
    "6": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.4, "y": 0.4},
                                {"x": 0.4, "y": 0.2},
                                {"x": 0.6, "y": 0.2},
                                {"x": 0.6, "y": 0.4},
                            ]
                        }
                    ],
                }
            ]
        }
    },
    "7": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_3}],
                }
            ]
        }
    },
    "8": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.4, "y": 0.3},
                                {"x": 0.4, "y": 0.1},
                                {"x": 0.6, "y": 0.1},
                                {"x": 0.6, "y": 0.3},
                            ]
                        }
                    ],
                }
            ]
        }
    },
    "9": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103085506560-87322",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_4}],
                }
            ]
        }
    },
}
