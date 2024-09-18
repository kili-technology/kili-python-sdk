import os
import tempfile

from kili.llm.presentation.client.llm import LlmClientMethods

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

mock_raw_asset_content = """{
    "prompts": [
        {
            "prompt": "BLABLABLA",
            "completions": [
                {
                    "content": "response A1"
                },
                {
                    "content": "response B1"
                }
            ]
        },
        {
            "prompt": "BLIBLIBLI",
            "completions": [
                {
                    "content": "response A2"
                },
                {
                    "content": "response B2"
                }
            ]
        }
    ],
    "type": "markdown",
    "version": "0.1"
}
"""

expected_export = [
    {
        "raw_data": [
            {
                "role": "user",
                "content": "BLABLABLA",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response A1",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response B1",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "user",
                "content": "BLIBLIBLI",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response A2",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response B2",
                "id": None,
                "chat_id": None,
                "model": None,
            },
        ],
        "status": "LABELED",
        "external_id": "asset#0",
        "metadata": {},
        "labels": [
            {
                "author": "test+admin@kili-technology.com",
                "created_at": "2024-08-05T13:03:00.051Z",
                "label_type": "DEFAULT",
                "label": {"CLASSIFICATION_JOB": ["A_BETTER_THAN_B"]},
            }
        ],
    },
    {
        "raw_data": [
            {
                "role": "user",
                "content": "BLABLABLA",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response A1",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response B1",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "user",
                "content": "BLIBLIBLI",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response A2",
                "id": None,
                "chat_id": None,
                "model": None,
            },
            {
                "role": "assistant",
                "content": "response B2",
                "id": None,
                "chat_id": None,
                "model": None,
            },
        ],
        "status": "LABELED",
        "external_id": "asset#1",
        "metadata": {},
        "labels": [
            {
                "author": "test+admin@kili-technology.com",
                "created_at": "2024-08-05T13:03:03.061Z",
                "label_type": "DEFAULT",
                "label": {"CLASSIFICATION_JOB": ["B_BETTER_THAN_A"]},
            }
        ],
    },
]


def test_export_static(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_RLHF",
        "title": "Test project",
        "id": "project_id",
        "dataConnections": None,
    }
    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.count_assets.return_value = 3
    kili_api_gateway.get_project.return_value = get_project_return_val

    kili_llm = LlmClientMethods(kili_api_gateway)
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(mock_raw_asset_content)
        for mocked_asset in mock_fetch_assets:
            mocked_asset["content"] = path
        kili_api_gateway.list_assets.return_value = mock_fetch_assets
        result = kili_llm.export(project_id="project_id")
        assert result == expected_export
    finally:
        os.remove(path)
