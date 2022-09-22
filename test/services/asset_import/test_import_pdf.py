from test.services.asset_import.base import ImportTestCase
from test.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from unittest.mock import MagicMock, patch

from kili.queries.asset import QueriesAsset
from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch.object(
    QueriesProject,
    "projects",
    MagicMock(return_value=[{"inputType": "PDF"}]),
)
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
class PDFTestCase(ImportTestCase):
    def test_upload_from_one_local_pdf(self):
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"], ["local pdf file"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_pdf(self):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_uplaod_from_several_batches(self):
        self.assert_upload_several_batches()
