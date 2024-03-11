"""Mocks for split video export."""

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
fake_bbox_norm_vertices = [
    {"x": 0.3596095126437537, "y": 0.7733564721502021},
    {"x": 0.3596095126437537, "y": 0.5060881610065724},
    {"x": 0.5183668894630696, "y": 0.5060881610065724},
    {"x": 0.5183668894630696, "y": 0.7733564721502021},
]

fake_bbox_norm_vertices2 = [
    {"x": 0.03345566648990772, "y": 0.34851316730689763},
    {"x": 0.03345566648990772, "y": 0.08124485616326804},
    {"x": 0.19221304330922367, "y": 0.08124485616326804},
    {"x": 0.19221304330922367, "y": 0.34851316730689763},
]

fake_bbox_norm_vertices3 = [
    {"x": 0.3885761484176185, "y": 0.305139673330994},
    {"x": 0.3885761484176185, "y": 0.03787136218736453},
    {"x": 0.5473335252369345, "y": 0.03787136218736453},
    {"x": 0.5473335252369345, "y": 0.305139673330994},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "a6cbf99c-af72-4cfa-8cb9-7a31b0f50748",
        "job": "JOB_0",
        "path": [],
        "labelId": "cltgdlxpr00jmxjwufgapd9i2",
        "frames": [{"start": 0, "end": 1}, {"start": 4, "end": 8}, {"start": 10, "end": 10}],
        "keyAnnotations": [
            {
                "id": "a6cbf99c-af72-4cfa-8cb9-7a31b0f50748-0",
                "frame": 0,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices]]},
            },
            {
                "id": "a6cbf99c-af72-4cfa-8cb9-7a31b0f50748-5",
                "frame": 5,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices2]]},
            },
            {
                "id": "a6cbf99c-af72-4cfa-8cb9-7a31b0f50748-7",
                "frame": 7,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices3]]},
            },
        ],
        "name": "Train 2",
        "mid": "20240306141046672-1",
        "category": "OBJECT_A",
    }
]

expected_json_resp = {
    "0": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                }
            ]
        },
        "ANNOTATION_JOB_COUNTER": {"JOB_0": {"OBJECT_A": 1}},
        "ANNOTATION_NAMES_JOB": {"20240306141046672-1": "Train 2"},
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.45313612023230043, "y": 0.6883878111815411},
                                {"x": 0.45313612023230043, "y": 0.4211195000379115},
                                {"x": 0.2943787434129844, "y": 0.4211195000379115},
                                {"x": 0.2943787434129844, "y": 0.6883878111815411},
                            ]
                        }
                    ],
                }
            ]
        }
    },
    "2": {},
    "3": {},
    "4": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.2574438125399928, "y": 0.4334818282755585},
                                {"x": 0.2574438125399928, "y": 0.1662135171319289},
                                {"x": 0.0986864357206769, "y": 0.1662135171319289},
                                {"x": 0.0986864357206769, "y": 0.4334818282755585},
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
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices2}],
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
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.3697732842730791, "y": 0.3268264203189458},
                                {"x": 0.3697732842730791, "y": 0.05955810917531629},
                                {"x": 0.2110159074537631, "y": 0.05955810917531629},
                                {"x": 0.2110159074537631, "y": 0.3268264203189458},
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
                    "children": {},
                    "isKeyFrame": True,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices3}],
                }
            ]
        }
    },
    "8": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices3}],
                }
            ]
        }
    },
    "9": {},
    "10": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices3}],
                }
            ]
        }
    },
}
