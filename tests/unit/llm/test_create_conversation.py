from kili_formats.types import ChatItemRole

from kili.llm.presentation.client.llm import LlmClientMethods


def test_create_conversation(mocker):
    mock_get_current_user = {"id": "user_id"}
    mock_llm_asset = {"id": "asset_id", "latestLabel": {"id": "label_id"}}
    mock_chat_item = [
        {
            "asset_id": "asset_id",
            "label_id": "label_id",
            "parent_id": None,
            "prompt": "prompt text",
            "role": ChatItemRole.USER,
        }
    ]

    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_current_user.return_value = mock_get_current_user
    kili_api_gateway.create_llm_asset.return_value = mock_llm_asset
    kili_api_gateway.create_chat_item.return_value = mock_chat_item

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.create_conversation(project_id="project_id", initial_prompt="prompt text")

    assert result == mock_chat_item

    kili_api_gateway.get_current_user.assert_called_once_with(["id"])
    kili_api_gateway.create_llm_asset.assert_called_once_with(
        project_id="project_id", author_id="user_id", label_type="PREDICTION"
    )
    kili_api_gateway.create_chat_item.assert_called_once_with(
        asset_id="asset_id",
        label_id="label_id",
        prompt="prompt text",
        parent_id=None,
        role=ChatItemRole.USER,
    )


def test_create_conversation_with_system_prompt(mocker):
    mock_get_current_user = {"id": "user_id"}
    mock_llm_asset = {"id": "asset_id", "latestLabel": {"id": "label_id"}}
    mock_system_chat_item = [
        {
            "id": "system_id",
            "asset_id": "asset_id",
            "label_id": "label_id",
            "prompt": "system prompt text",
            "role": ChatItemRole.SYSTEM,
        }
    ]
    mock_prompt_chat_item = [
        {
            "asset_id": "asset_id",
            "label_id": "label_id",
            "parent_id": "system_id",
            "prompt": "user prompt text",
            "role": ChatItemRole.USER,
        }
    ]

    kili_api_gateway = mocker.MagicMock()
    kili_api_gateway.get_current_user.return_value = mock_get_current_user
    kili_api_gateway.create_llm_asset.return_value = mock_llm_asset
    kili_api_gateway.create_chat_item.side_effect = [mock_system_chat_item, mock_prompt_chat_item]

    kili_llm = LlmClientMethods(kili_api_gateway)

    result = kili_llm.create_conversation(
        project_id="project_id",
        initial_prompt="user prompt text",
        system_prompt="system prompt text",
    )

    assert result == mock_system_chat_item + mock_prompt_chat_item

    kili_api_gateway.get_current_user.assert_called_once_with(["id"])
    kili_api_gateway.create_llm_asset.assert_called_once_with(
        project_id="project_id", author_id="user_id", label_type="PREDICTION"
    )
    kili_api_gateway.create_chat_item.assert_any_call(
        asset_id="asset_id",
        label_id="label_id",
        prompt="system prompt text",
        role=ChatItemRole.SYSTEM,
    )
    kili_api_gateway.create_chat_item.assert_any_call(
        asset_id="asset_id",
        label_id="label_id",
        prompt="user prompt text",
        role=ChatItemRole.USER,
        parent_id="system_id",
    )
