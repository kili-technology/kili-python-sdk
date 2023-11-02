json_interface = {
    "jobs": {
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "TRUCK": {
                        "children": ["CLASSIFICATION_JOB"],
                        "name": "Truck",
                        "color": "#5CE7B7",
                    }
                },
                "input": "radio",
            },
            "instruction": "Point job",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["marker"],
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
            "instruction": "Brand",
            "mlTask": "CLASSIFICATION",
            "required": 1,
            "isChild": True,
        },
    }
}

point_1 = {"x": 0.38633010142501345, "y": 0.5091000201848042}
point_2 = {"x": 0.2590335929094918, "y": 0.5051538679962855}

annotations = [
    {
        "id": "341834a0-6b7e-47d2-a290-a56833ed4a65",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh511r501sd084z0qz1hzxn",
        "frames": [{"start": 0, "end": 3}],
        "keyAnnotations": [
            {
                "id": "341834a0-6b7e-47d2-a290-a56833ed4a65-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"vertices": [[[point_1]]]},
            }
        ],
        "name": "Truck 1",
        "mid": "20231102130336664-88203",
        "category": "TRUCK",
    },
    {
        "id": "b1e7863d-f9f4-4804-8ede-5b34b3e38add",
        "job": "CLASSIFICATION_JOB",
        "path": [["341834a0-6b7e-47d2-a290-a56833ed4a65", "TRUCK"]],
        "labelId": "cloh511r501sd084z0qz1hzxn",
        "frames": [{"start": 0, "end": 3}],
        "keyAnnotations": [
            {
                "id": "b1e7863d-f9f4-4804-8ede-5b34b3e38add-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"categories": ["A"]},
            }
        ],
    },
    {
        "id": "5e963bda-2ab0-48e4-890b-6116b6610651",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh511r501sd084z0qz1hzxn",
        "frames": [{"start": 5, "end": 6}],
        "keyAnnotations": [
            {
                "id": "5e963bda-2ab0-48e4-890b-6116b6610651-5",
                "frame": 5,
                "isPrediction": False,
                "annotationValue": {"vertices": [[[point_2]]]},
            }
        ],
        "name": "Truck 2",
        "mid": "20231102130351045-28203",
        "category": "TRUCK",
    },
    {
        "id": "c0d1161c-6b97-4c28-873a-df1c7d4923e7",
        "job": "CLASSIFICATION_JOB",
        "path": [["5e963bda-2ab0-48e4-890b-6116b6610651", "TRUCK"]],
        "labelId": "cloh511r501sd084z0qz1hzxn",
        "frames": [{"start": 5, "end": 6}],
        "keyAnnotations": [
            {
                "id": "c0d1161c-6b97-4c28-873a-df1c7d4923e7-5",
                "frame": 5,
                "isPrediction": False,
                "annotationValue": {"categories": ["C", "B"]},
            }
        ],
    },
]

expected_json_resp = {
    "0": {
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
                    "point": point_1,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130336664-88203",
                    "type": "marker",
                }
            ]
        }
    },
    "1": {
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
                    "point": point_1,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130336664-88203",
                    "type": "marker",
                }
            ]
        }
    },
    "2": {
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
                    "point": point_1,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130336664-88203",
                    "type": "marker",
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
                    "point": point_1,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130336664-88203",
                    "type": "marker",
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
                                {"name": "C"},
                                {"name": "B"},
                            ],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "point": point_2,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130351045-28203",
                    "type": "marker",
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
                                {"name": "C"},
                                {"name": "B"},
                            ],
                            "isKeyFrame": False,
                        }
                    },
                    "isKeyFrame": False,
                    "point": point_2,
                    "categories": [{"name": "TRUCK"}],
                    "mid": "20231102130351045-28203",
                    "type": "marker",
                }
            ]
        }
    },
}
