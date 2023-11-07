json_interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": [], "name": "Train", "color": "#733AFB"},
                    "OBJECT_B": {"children": [], "name": "Car", "color": "#3CD876"},
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
        }
    }
}

bbox_car = [
    {"x": 0.3626470300732885, "y": 0.7432383833702492},
    {"x": 0.3626470300732885, "y": 0.5735538392639435},
    {"x": 0.495124210447, "y": 0.5735538392639435},
    {"x": 0.495124210447, "y": 0.7432383833702492},
]
bbox_train_1 = [
    {"x": 0.3537658783163916, "y": 0.556453846447029},
    {"x": 0.3537658783163916, "y": 0.4696384982996167},
    {"x": 0.4233349004120837, "y": 0.4696384982996167},
    {"x": 0.4233349004120837, "y": 0.556453846447029},
]
bbox_train_2 = [
    {"x": 0.2442316733146637, "y": 0.5248846289388791},
    {"x": 0.2442316733146637, "y": 0.4933154114307292},
    {"x": 0.2634741687879402, "y": 0.4933154114307292},
    {"x": 0.2634741687879402, "y": 0.5248846289388791},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "4e411541-0cc6-41a4-b2f2-b08004c6ffe8",
        "job": "JOB_0",
        "path": [],
        "labelId": "clooh26cv04e6085gdevdbpka",
        "keyAnnotations": [
            {
                "id": "4e411541-0cc6-41a4-b2f2-b08004c6ffe8-4",
                "frame": 4,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_train_2]]},
            }
        ],
        "frames": [{"start": 4, "end": 6}],
        "name": "Train 2",
        "mid": "20231107161254976-94354",
        "category": "OBJECT_A",
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "7bda6ed2-0174-4baf-9b25-8190546889b2",
        "job": "JOB_0",
        "path": [],
        "labelId": "clooh26cv04e6085gdevdbpka",
        "keyAnnotations": [
            {
                "id": "7bda6ed2-0174-4baf-9b25-8190546889b2-1",
                "frame": 1,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_car]]},
            }
        ],
        "frames": [{"start": 1, "end": 4}],
        "name": "Car 1",
        "mid": "20231107161234182-16067",
        "category": "OBJECT_B",
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "f81dbfaa-82d0-49c9-9a0e-1e620aad1b21",
        "job": "JOB_0",
        "path": [],
        "labelId": "clooh26cv04e6085gdevdbpka",
        "keyAnnotations": [
            {
                "id": "f81dbfaa-82d0-49c9-9a0e-1e620aad1b21-3",
                "frame": 3,
                "isPrediction": False,
                "annotationValue": {"vertices": [[bbox_train_1]]},
            }
        ],
        "frames": [{"start": 3, "end": 5}],
        "name": "Train 1",
        "mid": "20231107161223899-97216",
        "category": "OBJECT_A",
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"JOB_0": {"OBJECT_A": 2, "OBJECT_B": 1}},
        "ANNOTATION_NAMES_JOB": {
            "20231107161223899-97216": "Train 1",
            "20231107161234182-16067": "Car 1",
            "20231107161254976-94354": "Train 2",
        },
    },
    "1": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_car}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231107161234182-16067",
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
                    "boundingPoly": [{"normalizedVertices": bbox_car}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231107161234182-16067",
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
                    "boundingPoly": [{"normalizedVertices": bbox_car}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231107161234182-16067",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_train_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161223899-97216",
                    "type": "rectangle",
                },
            ]
        }
    },
    "4": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_train_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161254976-94354",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_car}],
                    "categories": [{"name": "OBJECT_B"}],
                    "mid": "20231107161234182-16067",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_train_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161223899-97216",
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
                    "boundingPoly": [{"normalizedVertices": bbox_train_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161254976-94354",
                    "type": "rectangle",
                },
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_train_1}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161223899-97216",
                    "type": "rectangle",
                },
            ]
        }
    },
    "6": {
        "JOB_0": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_train_2}],
                    "categories": [{"name": "OBJECT_A"}],
                    "mid": "20231107161254976-94354",
                    "type": "rectangle",
                }
            ]
        }
    },
}
