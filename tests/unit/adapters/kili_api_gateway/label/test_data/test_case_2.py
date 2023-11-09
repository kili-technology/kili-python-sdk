json_interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": ["JOB_1"], "name": "Train", "color": "#733AFB"},
                    "OBJECT_B": {"children": ["JOB_2"], "name": "Car", "color": "#3CD876"},
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
        "JOB_2": {
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

fake_bbox_vertices_1 = [
    {"x": 0.3596866461543229, "y": 0.5564430104705798},
    {"x": 0.3596866461543229, "y": 0.46699861580122337},
    {"x": 0.4248150923715665, "y": 0.46699861580122337},
    {"x": 0.4248150923715665, "y": 0.5564430104705798},
]

fake_bbox_vertices_2 = [
    {"x": 0.35524607027587446, "y": 0.782684714634246},
    {"x": 0.35524607027587446, "y": 0.5853809028636068},
    {"x": 0.5165869938595008, "y": 0.5853809028636068},
    {"x": 0.5165869938595008, "y": 0.782684714634246},
]

fake_bbox_vertices_3 = [
    {"x": 0.3241620391267354, "y": 0.6840328087489265},
    {"x": 0.3241620391267354, "y": 0.5419740642740661},
    {"x": 0.4240749963918251, "y": 0.5419740642740661},
    {"x": 0.4240749963918251, "y": 0.6840328087489265},
]

annotations = [
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "5c9efa8d-ded3-42df-9362-fdc55ea7e4ff",
        "job": "JOB_1",
        "path": [["33c26101-5b1f-48d3-b2b2-ffb04daec1d8", "OBJECT_A"]],
        "labelId": "clogvvow401rr08820aq6bhia",
        "keyAnnotations": [
            {
                "id": "5c9efa8d-ded3-42df-9362-fdc55ea7e4ff-4",
                "frame": 4,
                "annotationValue": {"categories": ["IS_THE OBJECT OCCLUDED?"]},
            }
        ],
        "frames": [{"start": 4, "end": 9}],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "7d8b1b46-73fc-434b-a8d1-a7734fce1d26",
        "job": "JOB_0",
        "path": [],
        "labelId": "clogvvow401rr08820aq6bhia",
        "keyAnnotations": [
            {
                "id": "7d8b1b46-73fc-434b-a8d1-a7734fce1d26-9",
                "frame": 9,
                "annotationValue": {"vertices": [[fake_bbox_vertices_3]]},
            }
        ],
        "frames": [{"start": 9, "end": 11}],
        "name": "Car 2",
        "mid": "20231102084526462-11",
        "category": "OBJECT_B",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "c94137a2-19ec-4872-8884-673d78e7b4c6",
        "job": "JOB_2",
        "path": [["7d8b1b46-73fc-434b-a8d1-a7734fce1d26", "OBJECT_B"]],
        "labelId": "clogvvow401rr08820aq6bhia",
        "keyAnnotations": [
            {
                "id": "c94137a2-19ec-4872-8884-673d78e7b4c6-9",
                "frame": 9,
                "annotationValue": {"categories": ["IS_THE OBJECT OCCLUDED?"]},
            }
        ],
        "frames": [{"start": 9, "end": 11}],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "af8e4bca-9442-49df-9321-17ffb008e659",
        "job": "JOB_0",
        "path": [],
        "labelId": "clogvvow401rr08820aq6bhia",
        "keyAnnotations": [
            {
                "id": "af8e4bca-9442-49df-9321-17ffb008e659-1",
                "frame": 1,
                "annotationValue": {"vertices": [[fake_bbox_vertices_2]]},
            }
        ],
        "frames": [{"start": 1, "end": 4}],
        "name": "Car 1",
        "mid": "20231102084443159-7",
        "category": "OBJECT_B",
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "33c26101-5b1f-48d3-b2b2-ffb04daec1d8",
        "job": "JOB_0",
        "path": [],
        "labelId": "clogvvow401rr08820aq6bhia",
        "keyAnnotations": [
            {
                "id": "33c26101-5b1f-48d3-b2b2-ffb04daec1d8-4",
                "frame": 4,
                "annotationValue": {"vertices": [[fake_bbox_vertices_1]]},
            }
        ],
        "frames": [{"start": 4, "end": 9}],
        "name": "Train 1",
        "mid": "20231102084459755-9",
        "category": "OBJECT_A",
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"JOB_0": {"OBJECT_A": 1, "OBJECT_B": 2}},
        "ANNOTATION_NAMES_JOB": {
            "20231102084526462-11": "Car 2",
            "20231102084443159-7": "Car 1",
            "20231102084459755-9": "Train 1",
        },
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_2}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084443159-7",
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_2}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084443159-7",
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
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_2}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084443159-7",
                    "type": "rectangle",
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_2}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084443159-7",
                    "type": "rectangle",
                },
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
                },
            ]
        }
    },
    "5": {
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
                }
            ]
        }
    },
    "6": {
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
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
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
                }
            ]
        }
    },
    "9": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_2": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_3}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084526462-11",
                    "type": "rectangle",
                },
                {
                    "children": {
                        "JOB_1": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231102084459755-9",
                    "type": "rectangle",
                },
            ]
        }
    },
    "10": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_2": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_3}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084526462-11",
                    "type": "rectangle",
                }
            ]
        }
    },
    "11": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "JOB_2": {
                            "categories": [{"name": "IS_THE OBJECT OCCLUDED?"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_vertices_3}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231102084526462-11",
                    "type": "rectangle",
                }
            ]
        }
    },
}
