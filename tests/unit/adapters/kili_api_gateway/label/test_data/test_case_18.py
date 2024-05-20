"""Mocks for split video export with multiple levels of nested jobs."""

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
        "__typename": "VideoClassificationAnnotation",
        "id": "20240514163156523-14",
        "job": "CLASSIFICATION_JOB",
        "path": [],
        "labelId": "clw91xo1q002wfxwuafkhartv",
        "keyAnnotations": [
            {
                "id": "20240514163156523-14-0",
                "frame": 0,
                "annotationValue": {"categories": ["MCA", "MCB"]},
            }
        ],
        "frames": [{"start": 0, "end": 0}],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "20240514163158501-15",
        "job": "CLASSIFICATION_JOB_0",
        "path": [["20240514163156523-14", "MCA"]],
        "labelId": "clw91xo1q002wfxwuafkhartv",
        "keyAnnotations": [
            {
                "id": "20240514163158501-15-0",
                "frame": 0,
                "annotationValue": {"categories": ["MCAMCD_1", "MCAMCD_2"]},
            }
        ],
        "frames": [{"start": 0, "end": 0}],
    },
    {
        "__typename": "VideoClassificationAnnotation",
        "id": "20240514163201282-16",
        "job": "CLASSIFICATION_JOB_1",
        "path": [["20240514163156523-14", "MCA"]],
        "labelId": "clw91xo1q002wfxwuafkhartv",
        "keyAnnotations": [
            {
                "id": "20240514163201282-16-0",
                "frame": 0,
                "annotationValue": {"categories": ["MCASCD_1"]},
            }
        ],
        "frames": [{"start": 0, "end": 0}],
    },
    {
        "__typename": "VideoTranscriptionAnnotation",
        "id": "20240514163203405-17",
        "job": "TRANSCRIPTION_JOB_0",
        "path": [["20240514163156523-14", "MCA"], ["20240514163201282-16", "MCASCD_1"]],
        "labelId": "clw91xo1q002wfxwuafkhartv",
        "keyAnnotations": [
            {"id": "20240514163203405-17-0", "frame": 0, "annotationValue": {"text": "a"}}
        ],
        "frames": [{"start": 0, "end": 0}],
    },
    {
        "__typename": "VideoTranscriptionAnnotation",
        "id": "20240514163205747-18",
        "job": "TRANSCRIPTION_JOB",
        "path": [["20240514163156523-14", "MCB"]],
        "labelId": "clw91xo1q002wfxwuafkhartv",
        "keyAnnotations": [
            {"id": "20240514163205747-18-0", "frame": 0, "annotationValue": {"text": "b"}}
        ],
        "frames": [{"start": 0, "end": 0}],
    },
]

expected_json_resp = {
    "0": {
        "CLASSIFICATION_JOB": {
            "categories": [
                {
                    "name": "MCA",
                    "children": {
                        "CLASSIFICATION_JOB_0": {
                            "categories": [{"name": "MCAMCD_1"}, {"name": "MCAMCD_2"}],
                            "isKeyFrame": True,
                        },
                        "CLASSIFICATION_JOB_1": {
                            "categories": [
                                {
                                    "name": "MCASCD_1",
                                    "children": {
                                        "TRANSCRIPTION_JOB_0": {"isKeyFrame": True, "text": "a"}
                                    },
                                }
                            ],
                            "isKeyFrame": True,
                        },
                    },
                },
                {
                    "name": "MCB",
                    "children": {"TRANSCRIPTION_JOB": {"isKeyFrame": True, "text": "b"}},
                },
            ],
            "isKeyFrame": True,
        }
    }
}
