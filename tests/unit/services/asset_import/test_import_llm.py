import json
from unittest.mock import patch

from kili.services.asset_import import import_assets
from kili.services.asset_import.helpers import process_json
from tests.unit.services.asset_import.base import ImportTestCase
from tests.unit.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
class LLMTestCase(ImportTestCase):
    def test_upload_from_one_local_file(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/llm/test_llm_file.json"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local llm file"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local llm file"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_file_in_chat_format(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/llm/test_llm_file_in_chat_format.json"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local llm file in chat format"}]
        import_assets(self.kili, self.project_id, assets)

        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local llm file in chat format"],
            ["unique_id"],
            [False],
            [""],
            [
                '{"chat_id": "6e4094947af4902cd252421aba9a077e8e4402dd", "models": "model-large_model-medium", "chat_item_ids": "0455df65c2d6bb821a9dc9108ac1d79964a0f571_4c28c86c4b22b3397691ce5cf27197fcf7e8fb2d_7326ff17cbfe7e3cb91b008cf0c496fcd17a1074_375b55d44af2c8c801992089c797df8e12605dfb_9231d8819ac96cc8a6c4b7780c301b796c3f8bf2"}'
            ],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_file_in_chat_format_with_given_json_metadata(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/llm/test_llm_file_in_chat_format.json"
        path = self.downloader(url)
        assets = [
            {
                "content": path,
                "external_id": "local llm file in chat format with json metadata",
                "json_metadata": '{ "customKey": "customValue" }',
            }
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local llm file in chat format with json metadata"],
            ["unique_id"],
            [False],
            [""],
            [
                '{"customKey": "customValue", "chat_id": "6e4094947af4902cd252421aba9a077e8e4402dd", "models": "model-large_model-medium", "chat_item_ids": "0455df65c2d6bb821a9dc9108ac1d79964a0f571_4c28c86c4b22b3397691ce5cf27197fcf7e8fb2d_7326ff17cbfe7e3cb91b008cf0c496fcd17a1074_375b55d44af2c8c801992089c797df8e12605dfb_9231d8819ac96cc8a6c4b7780c301b796c3f8bf2"}'
            ],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_text_file(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_dict(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        assets = [
            {
                "content": {
                    "prompt": "does it contain code ?",
                    "completions": ["first completion", "second completion", "#this is markdown"],
                    "type": "markdown",
                },
                "external_id": "dict",
            }
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"], ["dict"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_process_json(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/llm/test_llm_file_in_chat_format.json"
        path = self.downloader(url)

        with open(path) as file:
            data = json.load(file)

            processed_data = process_json(data)

            assert processed_data == (
                {
                    "prompts": [
                        {
                            "completions": [
                                {"content": "text of the assistant answer", "title": "assistant"}
                            ],
                            "prompt": "text of the user instructions",
                        },
                        {
                            "completions": [
                                {
                                    "content": "text of the assistant answer A",
                                    "title": "assistant_A",
                                },
                                {
                                    "content": "text of the assistant answer B",
                                    "title": "assistant_B",
                                },
                            ],
                            "prompt": "text of the user instructions",
                        },
                    ],
                    "type": "markdown",
                    "version": "0.1",
                },
                {
                    "chat_id": "6e4094947af4902cd252421aba9a077e8e4402dd",
                    "models": "model-large_model-medium",
                    "chat_item_ids": "0455df65c2d6bb821a9dc9108ac1d79964a0f571_4c28c86c4b22b3397691ce5cf27197fcf7e8fb2d_7326ff17cbfe7e3cb91b008cf0c496fcd17a1074_375b55d44af2c8c801992089c797df8e12605dfb_9231d8819ac96cc8a6c4b7780c301b796c3f8bf2",
                },
            )
