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
    {"x": 0.29603839189656206, "y": 0.64721534678296},
    {"x": 0.29603839189656206, "y": 0.5077846361219644},
    {"x": 0.39669144514139315, "y": 0.5077846361219644},
    {"x": 0.39669144514139315, "y": 0.64721534678296},
]
bbox_2 = [
    {"x": 0.36708760595173695, "y": 0.7235076224276555},
    {"x": 0.36708760595173695, "y": 0.5643461508240665},
    {"x": 0.4670005632168266, "y": 0.5643461508240665},
    {"x": 0.4670005632168266, "y": 0.7235076224276555},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "2209aa92-1c6c-4306-99af-a6e8a0278217",
        "job": "JOB_0",
        "path": [],
        "labelId": "cloic6byn03dx083f1ytb0km3",
        "frames": [{"start": 3, "end": 4}],
        "keyAnnotations": [
            {
                "id": "2209aa92-1c6c-4306-99af-a6e8a0278217-3",
                "frame": 3,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_1]]},
            }
        ],
        "name": "Train 3",
        "mid": "20231103090943036-54978",
        "category": "OBJECT_A",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "ea1e2f05-8610-411f-a29e-c5ee0b97548a",
        "job": "JOB_1",
        "path": [["2209aa92-1c6c-4306-99af-a6e8a0278217", "OBJECT_A"]],
        "labelId": "cloic6byn03dx083f1ytb0km3",
        "frames": [{"start": 3, "end": 4}],
        "keyAnnotations": [
            {
                "id": "ea1e2f05-8610-411f-a29e-c5ee0b97548a-3",
                "frame": 3,
                "isPrediction": False,
                "annotationValue": {"categories": ["IS_THE OBJECT OCCLUDED?"]},
            }
        ],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "73092b5e-4625-4b4f-a3cd-1c122cd3ce45",
        "job": "JOB_0",
        "path": [],
        "labelId": "cloic6byn03dx083f1ytb0km3",
        "frames": [{"start": 2, "end": 6}],
        "keyAnnotations": [
            {
                "id": "73092b5e-4625-4b4f-a3cd-1c122cd3ce45-2",
                "frame": 2,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_2]]},
            }
        ],
        "name": "Train 2",
        "mid": "20231103090918821-66388",
        "category": "OBJECT_A",
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"JOB_0": {"OBJECT_A": 2}},
        "ANNOTATION_NAMES_JOB": {
            "20231103090943036-54978": "Train 3",
            "20231103090918821-66388": "Train 2",
        },
    },
    "2": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090918821-66388",
                    "type": "rectangle",
                }
            ]
        }
    },
    "3": {
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
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090943036-54978",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090918821-66388",
                    "type": "rectangle",
                },
            ]
        }
    },
    "4": {
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
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090943036-54978",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090918821-66388",
                    "type": "rectangle",
                },
            ]
        }
    },
    "5": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090918821-66388",
                    "type": "rectangle",
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
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231103090918821-66388",
                    "type": "rectangle",
                }
            ]
        }
    },
}
