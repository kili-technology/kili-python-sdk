json_interface = {
    "jobs": {
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "A": {"children": ["CLASSIFICATION_JOB"], "color": "#472CED", "name": "A"}
                },
                "input": "radio",
            },
            "instruction": "BBOX Job 1",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["rectangle"],
            "isChild": False,
        },
        "OBJECT_DETECTION_JOB_0": {
            "content": {
                "categories": {
                    "A": {"children": ["CLASSIFICATION_JOB_0"], "color": "#5CE7B7", "name": "A"}
                },
                "input": "radio",
            },
            "instruction": "BBOX Job 2",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["rectangle"],
            "isChild": False,
        },
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "A": {"children": [], "name": "A"},
                    "B": {"children": [], "name": "B"},
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
            "content": {
                "categories": {
                    "A": {"children": [], "name": "A"},
                    "B": {"children": [], "name": "B"},
                },
                "input": "radio",
            },
            "instruction": "Classif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
    }
}

bbox_1 = [
    {"x": 0.3004789677750105, "y": 0.7300845427418534},
    {"x": 0.3004789677750105, "y": 0.5630307667612269},
    {"x": 0.48476286673062036, "y": 0.5630307667612269},
    {"x": 0.48476286673062036, "y": 0.7300845427418534},
]

bbox_2 = [
    {"x": 0.3767088536883752, "y": 0.5511923101956706},
    {"x": 0.3767088536883752, "y": 0.48410772299085214},
    {"x": 0.4477580677435501, "y": 0.48410772299085214},
    {"x": 0.4477580677435501, "y": 0.5511923101956706},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "75b1557f-42e7-44de-bb9a-e920c80df1db",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloib2vih01p0083fha217rkv",
        "keyAnnotations": [
            {
                "id": "75b1557f-42e7-44de-bb9a-e920c80df1db-2",
                "frame": 2,
                "annotationValue": {"vertices": [[bbox_1]]},
            }
        ],
        "frames": [{"start": 2, "end": 8}],
        "name": "A 1",
        "mid": "20231103084052882-30220",
        "category": "A",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "eab16f75-fc3d-45b5-9b4e-9f9cbcf8958f",
        "job": "CLASSIFICATION_JOB",
        "path": [["75b1557f-42e7-44de-bb9a-e920c80df1db", "A"]],
        "labelId": "cloib2vih01p0083fha217rkv",
        "keyAnnotations": [
            {
                "id": "eab16f75-fc3d-45b5-9b4e-9f9cbcf8958f-2",
                "frame": 2,
                "annotationValue": {"categories": ["A"]},
            },
            {
                "id": "eab16f75-fc3d-45b5-9b4e-9f9cbcf8958f-5",
                "frame": 5,
                "annotationValue": {"categories": ["A", "B"]},
            },
            {
                "id": "eab16f75-fc3d-45b5-9b4e-9f9cbcf8958f-8",
                "frame": 8,
                "annotationValue": {"categories": ["A", "B", "C"]},
            },
        ],
        "frames": [{"start": 2, "end": 8}],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "71f953d3-18af-42f2-8d37-c89e685eafb1",
        "job": "OBJECT_DETECTION_JOB_0",
        "path": [],
        "labelId": "cloib2vih01p0083fha217rkv",
        "keyAnnotations": [
            {
                "id": "71f953d3-18af-42f2-8d37-c89e685eafb1-6",
                "frame": 6,
                "annotationValue": {"vertices": [[bbox_2]]},
            }
        ],
        "frames": [{"start": 6, "end": 10}],
        "name": "A 1",
        "mid": "20231103084134382-18666",
        "category": "A",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "3dd700ec-1c8e-447a-b149-1e0f47516ad1",
        "job": "CLASSIFICATION_JOB_0",
        "path": [["71f953d3-18af-42f2-8d37-c89e685eafb1", "A"]],
        "labelId": "cloib2vih01p0083fha217rkv",
        "keyAnnotations": [
            {
                "id": "3dd700ec-1c8e-447a-b149-1e0f47516ad1-8",
                "frame": 8,
                "annotationValue": {"categories": ["A"]},
            },
            {
                "id": "3dd700ec-1c8e-447a-b149-1e0f47516ad1-10",
                "frame": 10,
                "annotationValue": {"categories": ["B"]},
            },
        ],
        "frames": [{"start": 8, "end": 10}],
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {
            "OBJECT_DETECTION_JOB": {"A": 1},
            "OBJECT_DETECTION_JOB_0": {"A": 1},
        },
        "ANNOTATION_NAMES_JOB": {
            "20231103084052882-30220": "A 1",
            "20231103084134382-18666": "A 1",
        },
    },
    "1": {},
    "2": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "A"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
                    "type": "rectangle",
                }
            ]
        }
    },
    "3": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "A"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
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
                            "categories": [{"name": "A"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
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
                                {"name": "A"},
                                {"name": "B"},
                            ],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
                    "type": "rectangle",
                }
            ]
        }
    },
    "6": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {"name": "A"},
                                {"name": "B"},
                            ],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
                    "type": "rectangle",
                }
            ]
        },
        "OBJECT_DETECTION_JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084134382-18666",
                    "type": "rectangle",
                }
            ]
        },
    },
    "7": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {"name": "A"},
                                {"name": "B"},
                            ],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
                    "type": "rectangle",
                }
            ]
        },
        "OBJECT_DETECTION_JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084134382-18666",
                    "type": "rectangle",
                }
            ]
        },
    },
    "8": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [
                                {"name": "A"},
                                {"name": "B"},
                                {"name": "C"},
                            ],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084052882-30220",
                    "type": "rectangle",
                }
            ]
        },
        "OBJECT_DETECTION_JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "A"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084134382-18666",
                    "type": "rectangle",
                }
            ]
        },
    },
    "9": {
        "OBJECT_DETECTION_JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "A"}],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084134382-18666",
                    "type": "rectangle",
                }
            ]
        }
    },
    "10": {
        "OBJECT_DETECTION_JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "B"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                    "categories": [{"name": "A"}],
                    "mid": "20231103084134382-18666",
                    "type": "rectangle",
                }
            ]
        }
    },
}
