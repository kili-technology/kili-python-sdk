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
    {"x": 0.3596095126437537, "y": 0.7733564721502021},
    {"x": 0.3596095126437537, "y": 0.5060881610065724},
    {"x": 0.5183668894630696, "y": 0.5060881610065724},
    {"x": 0.5183668894630696, "y": 0.7733564721502021},
]

fake_bbox_norm_vertices2 = [
    {"x": 0.3411479741822152, "y": 0.7715331103268402},
    {"x": 0.3411479741822152, "y": 0.5042647991832107},
    {"x": 0.49990535100153116, "y": 0.5042647991832107},
    {"x": 0.49990535100153116, "y": 0.7715331103268402},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "274e42ea-38b8-4847-805d-d373fd8d33da",
        "job": "JOB_0",
        "path": [],
        "labelId": "cltg3lf5r004gxjwuh3un5rax",
        "keyAnnotations": [
            {
                "id": "274e42ea-38b8-4847-805d-d373fd8d33da-0",
                "frame": 0,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices]]},
            },
            {
                "id": "274e42ea-38b8-4847-805d-d373fd8d33da-5",
                "frame": 5,
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices2]]},
            },
        ],
        "frames": [{"start": 0, "end": 1}, {"start": 4, "end": 6}],
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
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.514674581770762, "y": 0.7729917997855298},
                                {"x": 0.514674581770762, "y": 0.5057234886419},
                                {"x": 0.35591720495144596, "y": 0.5057234886419},
                                {"x": 0.35591720495144596, "y": 0.7729917997855298},
                            ]
                        }
                    ],
                }
            ]
        },
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
                                {"x": 0.5035976586938389, "y": 0.7718977826915127},
                                {"x": 0.5035976586938389, "y": 0.5046294715478831},
                                {"x": 0.344840281874523, "y": 0.5046294715478831},
                                {"x": 0.344840281874523, "y": 0.7718977826915127},
                            ]
                        }
                    ],
                }
            ]
        },
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
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices2}],
                }
            ]
        }
    },
}
