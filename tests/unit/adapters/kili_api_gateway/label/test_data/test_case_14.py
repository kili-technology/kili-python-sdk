json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "CHOICE_1": {"children": [], "name": "Choice 1"},
                    "CHOICE_2": {"children": [], "name": "Choice 2"},
                },
                "input": "radio",
            },
            "instruction": "Single Choice Classif",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "Transcription Text",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": False,
        },
    }
}

annotations = [
    {
        "id": "8be13b44-dfb5-4456-83b4-710b902f2fa3",
        "job": "CLASSIFICATION_JOB",
        "path": [],
        "labelId": "clr53q1as0208kjba8jwcavcx",
        "annotationValue": {
            "categories": ["Choice 1"],
            "id": "8be13b44-dfb5-4456-83b4-710b902f2fa3",
            "isPrediction": False,
            "__typename": "ClassificationAnnotationValue",
        },
        "__typename": "ClassificationAnnotation",
    },
    {
        "id": "b36e3e67-3539-4b72-9cb0-dae699fcc9c5",
        "job": "TRANSCRIPTION_JOB",
        "path": [],
        "labelId": "clr53q1as0208kjba8jwcavcx",
        "annotationValue": {
            "id": "b36e3e67-3539-4b72-9cb0-dae699fcc9c5",
            "isPrediction": False,
            "text": "Test Transcription",
            "__typename": "TranscriptionAnnotationValue",
        },
        "__typename": "TranscriptionAnnotation",
    },
]

assets = [
    {
        "content": "./fake_path_to_asset.csv",
        "externalId": "Click here to start",
        "id": "clr4rvcyt00023b6zme74rmxd",
        "isHoneypot": False,
        "isProcessingAuthorized": True,
        "jsonContent": "",
        "jsonMetadata": "{}",
        "latestLabel": {
            "annotations": annotations,
            "author": {
                "id": "user-1",
                "email": "test+admin@kili-technology.com",
                "firstname": "Test",
                "lastname": "Admin",
                "__typename": "User",
            },
            "createdAt": "2024-01-08T10:21:00.624Z",
            "honeypotMark": None,
            "isHoneypot": False,
            "isLatestLabelForUser": True,
            "isSentBackToQueue": False,
            "jsonResponse": "{}",
            "labelType": "DEFAULT",
            "modelName": None,
            "numberOfAnnotations": 0,
            "reviewScore": None,
            "totalSecondsToLabel": 10,
            "__typename": "Label",
        },
        "ocrMetadata": None,
        "status": "LABELED",
        "skipped": False,
        "projectId": "clr4ru09f01mnkjbadmvzb6vt",
        "toBeLabeledBy": [],
        "__typename": "Asset",
    }
]


expected_json_resp = {
    "CLASSIFICATION_JOB": {"categories": [{"name": "Choice 1"}]},
    "TRANSCRIPTION_JOB": {"text": "Test Transcription"},
}
