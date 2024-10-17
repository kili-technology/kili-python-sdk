mock_json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "A_BETTER_THAN_B": {
                        "children": [],
                        "name": "A better than B",
                        "id": "category1",
                    },
                    "B_BETTER_THAN_A": {
                        "children": [],
                        "name": "B better than A",
                        "id": "category2",
                    },
                    "TIE": {"children": [], "name": "Tie", "id": "category3"},
                },
                "input": "radio",
            },
            "instruction": "Compare",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
        "TRANSCRIPTION_JOB": {
            "content": {"input": "markdown"},
            "instruction": "",
            "mlTask": "TRANSCRIPTION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
    }
}
