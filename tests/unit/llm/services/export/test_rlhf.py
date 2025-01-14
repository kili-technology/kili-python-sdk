import os
import tempfile

from kili.llm.presentation.client.llm import LlmClientMethods
from tests.unit.services.export.fakes.llm_json_interface import mock_json_interface
from tests.unit.services.export.fakes.llm_project_assets import mock_fetch_assets
from tests.unit.services.export.fakes.llm_raw_asset_content import mock_raw_asset_content

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
                "label": {"conversation": {"CLASSIFICATION_JOB": ["A_BETTER_THAN_B"]}},
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
                "label": {"conversation": {"CLASSIFICATION_JOB": ["B_BETTER_THAN_A"]}},
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
