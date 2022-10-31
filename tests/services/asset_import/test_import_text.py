from unittest.mock import MagicMock, patch

from kili.queries.asset import QueriesAsset
from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets
from tests.services.asset_import.base import ImportTestCase
from tests.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch.object(
    QueriesProject,
    "projects",
    MagicMock(return_value=[{"inputType": "TEXT"}]),
)
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
class TextTestCase(ImportTestCase):
    def test_upload_from_one_local_text_file(self):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/texts/test_text_file.txt"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local text file"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local text file"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_text_file(
        self,
    ):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_raw_text(self):
        assets = [{"content": "this is raw text", "external_id": "raw text"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["raw text"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_rich_text(self):
        json_content = [
            {
                "children": [
                    {
                        "id": "1",
                        "underline": True,
                        "text": "A rich text asset",
                    }
                ]
            }
        ]
        assets = [{"json_content": json_content, "external_id": "rich text", "id": "unique_id"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            [""],
            ["rich text"],
            ["unique_id"],
            [False],
            ["https://signed_url?id=id"],
            ["{}"],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_uplaod_from_several_batches(self):
        self.assert_upload_several_batches()
