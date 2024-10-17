mock_fetch_assets = [
    {
        "labels": [
            {
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "jsonResponse": {
                    "CLASSIFICATION_JOB": {"categories": [{"name": "A_BETTER_THAN_B"}]}
                },
                "createdAt": "2024-08-05T13:03:00.051Z",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "content": "https://storage.googleapis.com/label-public-staging/demo-projects/LLM/01.json",
        "externalId": "asset#0",
        "jsonMetadata": {},
        "status": "LABELED",
    },
    {
        "labels": [
            {
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "jsonResponse": {
                    "CLASSIFICATION_JOB": {"categories": [{"name": "B_BETTER_THAN_A"}]}
                },
                "createdAt": "2024-08-05T13:03:03.061Z",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": False,
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "content": "https://storage.googleapis.com/label-public-staging/demo-projects/LLM/02.json",
        "externalId": "asset#1",
        "jsonMetadata": {},
        "status": "LABELED",
    },
    {
        "labels": [
            {
                "author": {
                    "id": "user-1",
                    "email": "test+admin@kili-technology.com",
                    "firstname": "Test",
                    "lastname": "Admin",
                },
                "jsonResponse": {
                    "CLASSIFICATION_JOB": {"categories": [{"name": "TIE"}]},
                    "TRANSCRIPTION_JOB": {"text": "There is only some formatting changes\n"},
                },
                "createdAt": "2024-08-05T13:03:16.028Z",
                "isLatestLabelForUser": True,
                "isSentBackToQueue": True,
                "labelType": "DEFAULT",
                "modelName": None,
            }
        ],
        "content": "https://storage.googleapis.com/label-public-staging/demo-projects/LLM/03.json",
        "externalId": "asset#2",
        "jsonMetadata": {},
        "status": "LABELED",
    },
]
