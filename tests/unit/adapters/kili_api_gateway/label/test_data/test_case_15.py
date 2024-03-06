"""Mocks for split video export."""

from collections import defaultdict

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
    {"x": 0.35, "y": 0.54},
    {"x": 0.35, "y": 0.46},
    {"x": 0.40, "y": 0.46},
    {"x": 0.40, "y": 0.54},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "55ad2c18-c063-4064-9f46-2e3fa3eed483",
        "job": "JOB_0",
        "path": [],
        "labelId": "cltftiw7n000qslwu4o1d9rj3",
        "frames": [{"start": 0, "end": 1}, {"start": 4, "end": 5}],
        "keyAnnotations": [
            {
                "id": "55ad2c18-c063-4064-9f46-2e3fa3eed483-0",
                "frame": 0,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices]]},
            }
        ],
        "name": "Train 2",
        "mid": "20240306141046672-1",
        "category": "OBJECT_A",
    }
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"JOB_0": defaultdict(int, {"OBJECT_A": 1})},
        "ANNOTATION_NAMES_JOB": {"20240306141046672-1": "Train 2"},
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
            ],
        },
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
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
                    "mid": "20240306141046672-1",
                    "type": "rectangle",
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                }
            ]
        }
    },
}
