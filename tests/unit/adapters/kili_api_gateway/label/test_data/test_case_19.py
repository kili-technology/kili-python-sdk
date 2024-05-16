"""Mocks for split llm export."""

json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "MCA": {
                        "children": ["CLASSIFICATION_JOB_0", "CLASSIFICATION_JOB_1"],
                        "name": "MCA",
                        "id": "category1",
                    },
                    "MCB": {"children": ["TRANSCRIPTION_JOB"], "name": "MCB", "id": "category2"},
                },
                "input": "checkbox",
            },
            "instruction": "MC",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
        "CLASSIFICATION_JOB_0": {
            "content": {
                "categories": {
                    "MCAMCD_1": {"children": [], "name": "MCAMCD1", "id": "category3"},
                    "MCAMCD_2": {"children": [], "name": "MCAMCD2", "id": "category4"},
                },
                "input": "multipleDropdown",
            },
            "instruction": "MCAMCD",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "CLASSIFICATION_JOB_1": {
            "content": {
                "categories": {
                    "MCASCD_1": {
                        "children": ["TRANSCRIPTION_JOB_0"],
                        "name": "MCASCD1",
                        "id": "category5",
                    },
                    "MCASCD_2": {"children": [], "name": "MCASCD2", "id": "category6"},
                },
                "input": "singleDropdown",
            },
            "instruction": "MCASCD",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "textField"},
            "instruction": "MCBT",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "TRANSCRIPTION_JOB_0": {
            "content": {"input": "textField"},
            "instruction": "MCASCD1T",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
    }
}


annotations = [
    {
        "__typename": "ClassificationAnnotation",
        "id": "20240514162922932-7",
        "job": "CLASSIFICATION_JOB",
        "path": [],
        "labelId": "clw91wkj4000afxwud60qa5iq",
        "annotationValue": {"categories": ["MCA", "MCB"]},
    },
    {
        "__typename": "ClassificationAnnotation",
        "id": "20240514162924690-8",
        "job": "CLASSIFICATION_JOB_0",
        "path": [["20240514162922932-7", "MCA"]],
        "labelId": "clw91wkj4000afxwud60qa5iq",
        "annotationValue": {"categories": ["MCAMCD_1", "MCAMCD_2"]},
    },
    {
        "__typename": "ClassificationAnnotation",
        "id": "20240514162932025-9",
        "job": "CLASSIFICATION_JOB_1",
        "path": [["20240514162922932-7", "MCA"]],
        "labelId": "clw91wkj4000afxwud60qa5iq",
        "annotationValue": {"categories": ["MCASCD_1"]},
    },
    {
        "__typename": "TranscriptionAnnotation",
        "id": "20240514162957261-12",
        "job": "TRANSCRIPTION_JOB_0",
        "path": [["20240514162922932-7", "MCA"], ["20240514162932025-9", "MCASCD_1"]],
        "labelId": "clw91wkj4000afxwud60qa5iq",
        "annotationValue": {"text": "a"},
    },
    {
        "__typename": "TranscriptionAnnotation",
        "id": "20240516113114061-1",
        "job": "TRANSCRIPTION_JOB",
        "path": [["20240514162922932-7", "MCB"]],
        "labelId": "clw91wkj4000afxwud60qa5iq",
        "annotationValue": {"text": "b"},
    },
]
expected_json_resp = {
    "CLASSIFICATION_JOB": {
        "categories": [
            {
                "name": "MCA",
                "children": {
                    "CLASSIFICATION_JOB_0": {
                        "categories": [{"name": "MCAMCD_1"}, {"name": "MCAMCD_2"}]
                    },
                    "CLASSIFICATION_JOB_1": {
                        "categories": [
                            {"name": "MCASCD_1", "children": {"TRANSCRIPTION_JOB_0": {"text": "a"}}}
                        ]
                    },
                },
            },
            {"name": "MCB", "children": {"TRANSCRIPTION_JOB": {"text": "b"}}},
        ]
    }
}
