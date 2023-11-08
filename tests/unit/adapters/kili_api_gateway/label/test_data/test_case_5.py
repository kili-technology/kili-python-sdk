json_interface = {
    "jobs": {
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "CAR": {"children": ["CLASSIFICATION_JOB_0"], "color": "#472CED", "name": "Car"}
                },
                "input": "radio",
            },
            "instruction": "POLYGON",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["polygon"],
            "isChild": False,
        },
        "CLASSIFICATION_JOB_0": {
            "content": {"categories": {"A": {"children": [], "name": "A"}}, "input": "radio"},
            "instruction": "Brand",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
        },
    }
}

bbox_vertices = [
    {"x": 0.4795821948724305, "y": 0.6971999411708638},
    {"x": 0.4788420988926891, "y": 0.5656615348869061},
    {"x": 0.3596866461543229, "y": 0.5630307667612269},
    {"x": 0.33970405470130494, "y": 0.7195614702391366},
]

polygon_vertices = [
    {"x": 0.43221605216898057, "y": 0.5538230783213498},
    {"x": 0.436656628047429, "y": 0.48016157080233335},
    {"x": 0.3537658783163916, "y": 0.5222538608131999},
]

annotations = [
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "db3f1827-cde6-4936-9e11-e71b02b849c6",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh714jn01yq0885bcoa7bon",
        "keyAnnotations": [
            {
                "id": "db3f1827-cde6-4936-9e11-e71b02b849c6-2",
                "frame": 2,
                "annotationValue": {"vertices": [[bbox_vertices]]},
            }
        ],
        "frames": [{"start": 2, "end": 5}],
        "name": "Car 1",
        "mid": "20231102135530134-87099",
        "category": "CAR",
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "id": "709f7b2a-6772-4c6d-ad95-02d7402ed47f",
        "job": "OBJECT_DETECTION_JOB",
        "path": [],
        "labelId": "cloh714jn01yq0885bcoa7bon",
        "keyAnnotations": [
            {
                "id": "709f7b2a-6772-4c6d-ad95-02d7402ed47f-3",
                "frame": 3,
                "annotationValue": {"vertices": [[polygon_vertices]]},
            }
        ],
        "frames": [{"start": 3, "end": 3}],
        "name": "Car 2",
        "mid": "20231102135542586-10862",
        "category": "CAR",
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "cb8347d3-3d07-4fbe-8eac-440f0c96b50b",
        "job": "CLASSIFICATION_JOB_0",
        "path": [["709f7b2a-6772-4c6d-ad95-02d7402ed47f", "CAR"]],
        "labelId": "cloh714jn01yq0885bcoa7bon",
        "keyAnnotations": [
            {
                "id": "cb8347d3-3d07-4fbe-8eac-440f0c96b50b-3",
                "frame": 3,
                "annotationValue": {"categories": ["A"]},
            }
        ],
        "frames": [{"start": 3, "end": 3}],
    },
]

expected_json_resp = {
    "0": {
        "ANNOTATION_JOB_COUNTER": {"OBJECT_DETECTION_JOB": {"CAR": 2}},
        "ANNOTATION_NAMES_JOB": {
            "20231102135530134-87099": "Car 1",
            "20231102135542586-10862": "Car 2",
        },
    },
    "1": {},
    "2": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231102135530134-87099",
                    "type": "polygon",
                }
            ]
        }
    },
    "3": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231102135530134-87099",
                    "type": "polygon",
                },
                {
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "A"}],
                            "isKeyFrame": True,
                        }
                    },
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": polygon_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231102135542586-10862",
                    "type": "polygon",
                },
            ]
        }
    },
    "4": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231102135530134-87099",
                    "type": "polygon",
                }
            ]
        }
    },
    "5": {
        "OBJECT_DETECTION_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": bbox_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231102135530134-87099",
                    "type": "polygon",
                }
            ]
        }
    },
}
