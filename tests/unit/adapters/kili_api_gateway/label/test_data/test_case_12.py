json_interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "CAR": {"children": ["CLASSIFICATION_JOB"], "name": "Car", "color": "#733AFB"}
                },
                "input": "radio",
            },
            "instruction": "Track objects",
            "isChild": False,
            "tools": ["rectangle"],
            "mlTask": "OBJECT_DETECTION",
            "models": {"tracking": {}},
            "isVisible": True,
            "required": 0,
        },
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "BLUE": {"children": ["TRANSCRIPTION_JOB"], "name": "Blue"},
                    "RED": {"children": ["CLASSIFICATION_JOB_0"], "name": "Red"},
                },
                "input": "radio",
            },
            "instruction": "Color",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Brand",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": True,
        },
        "CLASSIFICATION_JOB_0": {
            "content": {
                "categories": {"PURPLE_RED": {"children": [], "name": "Purple red"}},
                "input": "radio",
            },
            "instruction": "Pink red",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
    }
}

bbox_1 = [
    {"x": 0.3752286617288924, "y": 0.74060761524457},
    {"x": 0.3752286617288924, "y": 0.5669769189497456},
    {"x": 0.5077058421026039, "y": 0.5669769189497456},
    {"x": 0.5077058421026039, "y": 0.74060761524457},
]
bbox_2 = [
    {"x": 0.3515455903771674, "y": 0.724823006490495},
    {"x": 0.3515455903771674, "y": 0.5511923101956707},
    {"x": 0.48402277075087896, "y": 0.5511923101956707},
    {"x": 0.48402277075087896, "y": 0.724823006490495},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "0549e9c5-8642-448a-8245-47a8e79d9fe0",
        "job": "JOB_0",
        "path": [],
        "labelId": "clooim1qh05qx085gbz9j9rek",
        "frames": [{"start": 0, "end": 1}],
        "keyAnnotations": [
            {
                "id": "0549e9c5-8642-448a-8245-47a8e79d9fe0-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_1]]},
            },
            {
                "id": "0549e9c5-8642-448a-8245-47a8e79d9fe0-1",
                "frame": 1,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_2]]},
            },
        ],
        "name": "Car 2",
        "mid": "20231107165516728-66260",
        "category": "CAR",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "dc518c4d-a1e9-4672-b763-cea144f2797b",
        "job": "CLASSIFICATION_JOB",
        "path": [["0549e9c5-8642-448a-8245-47a8e79d9fe0", "CAR"]],
        "labelId": "clooim1qh05qx085gbz9j9rek",
        "frames": [{"start": 0, "end": 1}],
        "keyAnnotations": [
            {
                "id": "dc518c4d-a1e9-4672-b763-cea144f2797b-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"categories": ["BLUE"]},
            },
            {
                "id": "dc518c4d-a1e9-4672-b763-cea144f2797b-1",
                "frame": 1,
                "isPrediction": False,
                "annotationValue": {"categories": ["RED"]},
            },
        ],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "c6bc5b7e-ec44-4536-917e-bb20479d7819",
        "job": "CLASSIFICATION_JOB_0",
        "path": [
            ["0549e9c5-8642-448a-8245-47a8e79d9fe0", "CAR"],
            ["dc518c4d-a1e9-4672-b763-cea144f2797b", "RED"],
        ],
        "labelId": "clooim1qh05qx085gbz9j9rek",
        "frames": [{"start": 1, "end": 1}],
        "keyAnnotations": [
            {
                "id": "c6bc5b7e-ec44-4536-917e-bb20479d7819-1",
                "frame": 1,
                "isPrediction": False,
                "annotationValue": {"categories": ["PURPLE_RED"]},
            }
        ],
    },
    {
        "__typename": "VideoTranscriptionAnnotation",
        "id": "389d3431-93e7-4566-a249-1c08ffc2d2be",
        "job": "TRANSCRIPTION_JOB",
        "path": [
            ["0549e9c5-8642-448a-8245-47a8e79d9fe0", "CAR"],
            ["dc518c4d-a1e9-4672-b763-cea144f2797b", "BLUE"],
        ],
        "labelId": "clooim1qh05qx085gbz9j9rek",
        "frames": [{"start": 0, "end": 0}],
        "keyAnnotations": [
            {
                "id": "389d3431-93e7-4566-a249-1c08ffc2d2be-0",
                "frame": 0,
                "isPrediction": False,
                "annotationValue": {"text": "Bmw"},
            }
        ],
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"JOB_0": {"CAR": 1}},
        "ANNOTATION_NAMES_JOB": {"20231107165516728-66260": "Car 2"},
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "BLUE"}],
                            "isKeyFrame": True,
                        },
                        "TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "Bmw"},
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_1}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231107165516728-66260",
                    "type": "rectangle",
                }
            ]
        },
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {
                        "CLASSIFICATION_JOB": {
                            "categories": [{"name": "RED"}],
                            "isKeyFrame": True,
                        },
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "PURPLE_RED"}],
                            "isKeyFrame": True,
                        },
                    },
                    "isKeyFrame": True,
                    "categories": [{"name": "CAR"}],
                    "mid": "20231107165516728-66260",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": bbox_2}],
                }
            ]
        }
    },
}
