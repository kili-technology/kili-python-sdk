json_interface = {
    "jobs": {
        "BBOX_JOB": {
            "content": {
                "categories": {
                    "TRAIN": {"children": [], "name": "Train", "color": "#733AFB"},
                    "CAR": {"children": [], "name": "Car", "color": "#3CD876"},
                },
                "input": "radio",
            },
            "instruction": "BBox job",
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
                    "A": {"children": [], "name": "A"},
                    "B": {"children": [], "name": "B"},
                },
                "input": "radio",
            },
            "instruction": "Classif job",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Transcription",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": False,
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
        "labelId": "fake_label_id",
        "category": "TRAIN",
        "frames": [{"end": 4, "start": 0}],
        "id": "c28e7c80-35af-459a-97a7-ed7a0d11988d",
        "job": "BBOX_JOB",
        "keyAnnotations": [
            {
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices]]},
                "frame": 0,
                "id": "c28e7c80-35af-459a-97a7-ed7a0d11988d-0",
                "isPrediction": False,
            }
        ],
        "mid": "20231031123948352-1",
        "name": "TRAIN 1",
        "path": [],
    },
    {
        "__typename": "VideoObjectDetectionAnnotation",
        "category": "CAR",
        "labelId": "fake_label_id",
        "frames": [{"end": 16, "start": 14}],
        "id": "0a6042f9-2312-43b9-bf01-0ce62653f148",
        "job": "BBOX_JOB",
        "keyAnnotations": [
            {
                "annotationValue": {"vertices": [[fake_bbox_norm_vertices]]},
                "frame": 14,
                "id": "0a6042f9-2312-43b9-bf01-0ce62653f148-14",
                "isPrediction": False,
            }
        ],
        "mid": "20231031124001125-3",
        "name": "CAR 1",
        "path": [],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "labelId": "fake_label_id",
        "frames": [{"end": 8, "start": 6}],
        "id": "9cb16f2a-0907-4601-88cb-adcb4e7aec5c",
        "job": "CLASSIFICATION_JOB",
        "keyAnnotations": [
            {
                "annotationValue": {"categories": ["A"]},
                "frame": 6,
                "id": "9cb16f2a-0907-4601-88cb-adcb4e7aec5c-6",
                "isPrediction": False,
            }
        ],
        "path": [],
    },
    {
        "__typename": "VideoTranscriptionAnnotation",
        "labelId": "fake_label_id",
        "frames": [{"end": 9, "start": 4}, {"end": 14, "start": 12}],
        "id": "5a790a50-8d95-44fb-8941-93366c61d999",
        "job": "TRANSCRIPTION_JOB",
        "keyAnnotations": [
            {
                "annotationValue": {"text": "some text on frame 5"},
                "frame": 4,
                "id": "5a790a50-8d95-44fb-8941-93366c61d999-4",
                "isPrediction": False,
            },
            {
                "annotationValue": {"text": "some text on frame 13"},
                "frame": 12,
                "id": "5a790a50-8d95-44fb-8941-93366c61d999-12",
                "isPrediction": False,
            },
        ],
        "path": [],
    },
]

expected_json_resp = {
    "0": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "TRAIN"}],
                    "mid": "20231031123948352-1",
                    "type": "rectangle",
                }
            ]
        },
    },
    "1": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "TRAIN"}],
                    "mid": "20231031123948352-1",
                    "type": "rectangle",
                }
            ]
        }
    },
    "2": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "TRAIN"}],
                    "mid": "20231031123948352-1",
                    "type": "rectangle",
                }
            ]
        }
    },
    "3": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "TRAIN"}],
                    "mid": "20231031123948352-1",
                    "type": "rectangle",
                }
            ]
        }
    },
    "4": {
        "TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "some text on frame 5"},
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "TRAIN"}],
                    "mid": "20231031123948352-1",
                    "type": "rectangle",
                }
            ]
        },
    },
    "5": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 5"}},
    "6": {
        "CLASSIFICATION_JOB": {
            "categories": [{"name": "A"}],
            "isKeyFrame": True,
        },
        "TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 5"},
    },
    "7": {
        "CLASSIFICATION_JOB": {
            "categories": [{"name": "A"}],
            "isKeyFrame": False,
        },
        "TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 5"},
    },
    "8": {
        "CLASSIFICATION_JOB": {
            "categories": [{"name": "A"}],
            "isKeyFrame": False,
        },
        "TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 5"},
    },
    "9": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 5"}},
    "12": {"TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "some text on frame 13"}},
    "13": {"TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 13"}},
    "14": {
        "TRANSCRIPTION_JOB": {"isKeyFrame": False, "text": "some text on frame 13"},
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": True,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231031124001125-3",
                    "type": "rectangle",
                }
            ]
        },
    },
    "15": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231031124001125-3",
                    "type": "rectangle",
                }
            ]
        },
    },
    "16": {
        "BBOX_JOB": {
            "annotations": [
                {
                    "children": {},
                    "isKeyFrame": False,
                    "boundingPoly": [{"normalizedVertices": fake_bbox_norm_vertices}],
                    "categories": [{"name": "CAR"}],
                    "mid": "20231031124001125-3",
                    "type": "rectangle",
                }
            ]
        },
    },
}
