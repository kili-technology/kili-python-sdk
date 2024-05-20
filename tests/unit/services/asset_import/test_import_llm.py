from unittest.mock import patch

from kili.services.asset_import import import_assets
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
