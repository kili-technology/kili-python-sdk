import os
import tempfile
from unittest.mock import patch

from kili.presentation.client.label import LabelClientMethods

mock_json_interface = {
    "jobs": {
        "CLASSIFICATION_JOB": {
            "content": {
                "categories": {
                    "STEP_1": {
                        "children": ["STEP_1_RANKING", "STEP_1_QUALITY"],
                        "name": "Step 1",
                        "id": "category1",
                    },
                    "STEP_2": {
                        "children": ["STEP_2_RANKING", "STEP_2_QUALITY"],
                        "name": "Step 2",
                        "id": "category2",
                    },
                },
                "input": "checkbox",
            },
            "instruction": "Select the step",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": False,
            "isNew": False,
        },
        "STEP_1_RANKING": {
            "content": {
                "categories": {
                    "STEP_1_A_3": {
                        "children": [],
                        "name": "A is much better than B",
                        "id": "category21",
                    },
                    "STEP_1_A_2": {
                        "children": [],
                        "name": "A is better than B",
                        "id": "category22",
                    },
                    "STEP_1_A_1": {
                        "children": [],
                        "name": "A is slightly better than B",
                        "id": "category23",
                    },
                    "STEP_1_TIE": {"children": [], "name": "Tie", "id": "category24"},
                    "STEP_1_B_1": {
                        "children": [],
                        "name": "B is slightly better than A",
                        "id": "category25",
                    },
                    "STEP_1_B_2": {
                        "children": [],
                        "name": "B is better than A",
                        "id": "category26",
                    },
                    "STEP_1_B_3": {
                        "children": [],
                        "name": "B is much better than A",
                        "id": "category27",
                    },
                },
                "input": "singleDropdown",
            },
            "instruction": "Ranking",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "STEP_1_QUALITY": {
            "content": {
                "categories": {
                    "STEP_1_GOOD": {
                        "children": [],
                        "name": "Both answers are very good",
                        "id": "category28",
                    },
                    "STEP_1_BAD": {
                        "children": [],
                        "name": "Both answers are very bad",
                        "id": "category29",
                    },
                },
                "input": "singleDropdown",
            },
            "instruction": "Overall quality",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "STEP_2_RANKING": {
            "content": {
                "categories": {
                    "STEP_2_A_3": {
                        "children": [],
                        "name": "A is much better than B",
                        "id": "category30",
                    },
                    "STEP_2_A_2": {
                        "children": [],
                        "name": "A is better than B",
                        "id": "category31",
                    },
                    "STEP_2_A_1": {
                        "children": [],
                        "name": "A is slightly better than B",
                        "id": "category32",
                    },
                    "STEP_2_TIE": {"children": [], "name": "Tie", "id": "category33"},
                    "STEP_2_B_1": {
                        "children": [],
                        "name": "B is slightly better than A",
                        "id": "category34",
                    },
                    "STEP_2_B_2": {
                        "children": [],
                        "name": "B is better than A",
                        "id": "category35",
                    },
                    "STEP_2_B_3": {
                        "children": [],
                        "name": "B is much better than A",
                        "id": "category36",
                    },
                },
                "input": "singleDropdown",
            },
            "instruction": "Ranking",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
        "STEP_2_QUALITY": {
            "content": {
                "categories": {
                    "STEP_2_GOOD": {
                        "children": [],
                        "name": "Both answers are very good",
                        "id": "category37",
                    },
                    "STEP_2_BAD": {
                        "children": [],
                        "name": "Both answers are very bad",
                        "id": "category38",
                    },
                },
                "input": "singleDropdown",
            },
            "instruction": "Overall quality",
            "mlTask": "CLASSIFICATION",
            "required": 0,
            "isChild": True,
            "isNew": False,
        },
    }
}

mock_fetch_assets = [
    {
        "pageResolutions": None,
        "resolution": None,
        "latestLabel": {
            "author": {
                "id": "cl7ugav7800hw0lqghawj9d30",
                "email": "jean.latapy@kili-technology.com",
                "firstname": "jean",
                "lastname": "latapy",
                "name": "jean latapy",
            },
            "jsonResponse": {
                "CLASSIFICATION_JOB": {
                    "categories": [
                        {
                            "name": "STEP_1",
                            "children": {
                                "STEP_1_RANKING": {"categories": [{"name": "STEP_1_B_3"}]}
                            },
                        },
                        {
                            "name": "STEP_2",
                            "children": {
                                "STEP_2_RANKING": {"categories": [{"name": "STEP_2_A_3"}]}
                            },
                        },
                    ]
                }
            },
            "createdAt": "2024-07-05T16:03:58.962Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "id": "cly8vy5t0000601u5ejzkw8rb",
        "externalId": "42d0c18601624413bb4bf6fd9a5436df",
        "content": "/tmp/content.json",
        "jsonContent": "",
        "jsonMetadata": {
            "chat_id": "global-chat-id",
            "models": "model-1___model-2",
            "chat_item_ids": "id_1___id_1_1___id_1_2___id_2___id_2_1___id_2_2",
        },
        "status": "LABELED",
    }
]

mock_raw_asset_content = """{
    "prompts": [
        {
            "prompt": "BLABLABLA",
            "completions": [
                {
                    "content": "Hello! How can I assist you today?",
                    "title": "Model A"
                },
                {
                    "content": "Hello! How can I assist you today? If you have any questions or need information, feel free to ask. I'm here to help!",
                    "title": "Model B"
                }
            ]
        },
        {
            "prompt": "BLIBLIBLI",
            "completions": [
                {
                    "content": "I apologize if I'm not understanding your message correctly. Could you please provide more context or let me know how I can assist you?",
                    "title": "Model A"
                },
                {
                    "content": "It seems like you're having a bit of fun! If you have any specific questions or if there's something particular you'd like to know about, just let me know. I'm here to provide information and assist you in any way I can!",
                    "title": "Model B"
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
        "0": {
            "raw_data": [
                {
                    "role": "user",
                    "content": "BLABLABLA",
                    "id": "id_1",
                    "chat_id": "global-chat-id",
                    "model": None,
                },
                {
                    "role": "Model A",
                    "content": "Hello! How can I assist you today?",
                    "id": "id_1_1",
                    "chat_id": "global-chat-id",
                    "model": "model-1",
                },
                {
                    "role": "Model B",
                    "content": "Hello! How can I assist you today? If you have any questions or need information, feel free to ask. I'm here to help!",
                    "id": "id_1_2",
                    "chat_id": "global-chat-id",
                    "model": "model-2",
                },
            ],
            "status": "LABELED",
            "external_id": "42d0c18601624413bb4bf6fd9a5436df",
            "metadata": {
                "chat_id": "global-chat-id",
                "chat_item_ids": "id_1___id_1_1___id_1_2___id_2___id_2_1___id_2_2",
                "models": "model-1___model-2",
            },
            "labels": [
                {
                    "author": "jean.latapy@kili-technology.com",
                    "created_at": "2024-07-05T16:03:58.962Z",
                    "label_type": "DEFAULT",
                    "label": {"RANKING": ["B_3"]},
                }
            ],
        },
        "1": {
            "raw_data": [
                {
                    "role": "user",
                    "content": "BLABLABLA",
                    "id": "id_1",
                    "chat_id": "global-chat-id",
                    "model": None,
                },
                {
                    "role": "Model B",
                    "content": "Hello! How can I assist you today? If you have any questions or need information, feel free to ask. I'm here to help!",
                    "id": "id_1_2",
                    "chat_id": "global-chat-id",
                    "model": "model-2",
                },
                {
                    "role": "user",
                    "content": "BLIBLIBLI",
                    "id": "id_2",
                    "chat_id": "global-chat-id",
                    "model": None,
                },
                {
                    "role": "Model A",
                    "content": "I apologize if I'm not understanding your message correctly. Could you please provide more context or let me know how I can assist you?",
                    "id": "id_2_1",
                    "chat_id": "global-chat-id",
                    "model": "model-1",
                },
                {
                    "role": "Model B",
                    "content": "It seems like you're having a bit of fun! If you have any specific questions or if there's something particular you'd like to know about, just let me know. I'm here to provide information and assist you in any way I can!",
                    "id": "id_2_2",
                    "chat_id": "global-chat-id",
                    "model": "model-2",
                },
            ],
            "status": "LABELED",
            "external_id": "42d0c18601624413bb4bf6fd9a5436df",
            "metadata": {
                "chat_id": "global-chat-id",
                "chat_item_ids": "id_1___id_1_1___id_1_2___id_2___id_2_1___id_2_2",
                "models": "model-1___model-2",
            },
            "labels": [
                {
                    "author": "jean.latapy@kili-technology.com",
                    "created_at": "2024-07-05T16:03:58.962Z",
                    "label_type": "DEFAULT",
                    "label": {"RANKING": ["A_3"]},
                }
            ],
        },
    }
]


def test_export_dynamic(mocker):
    get_project_return_val = {
        "jsonInterface": mock_json_interface,
        "inputType": "LLM_RLHF",
        "title": "",
        "id": "project_id",
        "dataConnections": None,
    }
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.count_assets.return_value = 1
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(mock_raw_asset_content)
        mock_fetch_assets[0]["content"] = path
        with patch("kili.services.export.format.base.fetch_assets") as mocked_fetch_assets:
            mocked_fetch_assets.return_value = mock_fetch_assets
            result = kili.export_labels(
                project_id="project_id",
                fmt="llm_dynamic_v1",
                filename=None,
            )
            assert result == expected_export
    finally:
        os.remove(path)
