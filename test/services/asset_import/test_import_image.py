from test.services.asset_import.base import ImportTestCase
from test.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from unittest.mock import MagicMock, call, patch

from kili.queries.asset import QueriesAsset
from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch.object(
    QueriesProject,
    "projects",
    MagicMock(return_value=[{"inputType": "IMAGE"}]),
)
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
class PDFTestCase(ImportTestCase):
    def test_upload_from_one_local_image(self):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"], ["local image"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_image(
        self,
    ):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_tiff_image(self):
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local tiff image"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"], ["local tiff image"], ["{}"], "GEO_SATELLITE"
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_with_one_tiff_and_one_basic_image(self):
        url_tiff = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        url_basic = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_basic = self.downloader(url_basic)
        path_tiff = self.downloader(url_tiff)
        assets = [
            {"content": path_basic, "external_id": "local basic image"},
            {"content": path_tiff, "external_id": "local tiff image"},
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters_sync = self.get_expected_sync_call(
            ["https://signed_url?id=id"], ["local basic image"], [False], [""], ["{}"], ["TODO"]
        )
        expected_parameters_async = self.get_expected_async_call(
            ["https://signed_url?id=id"], ["local tiff image"], ["{}"], "GEO_SATELLITE"
        )
        calls = [call(*expected_parameters_sync), call(*expected_parameters_async)]
        self.auth.client.execute.assert_has_calls(calls, any_order=True)

    def test_uplaod_from_several_batches(self):
        self.assert_upload_several_batches()
