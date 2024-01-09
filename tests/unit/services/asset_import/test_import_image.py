from unittest.mock import MagicMock, call, patch

import pytest

from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import UploadFromLocalDataForbiddenError
from tests.unit.services.asset_import.base import ImportTestCase
from tests.unit.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
    organization_generator,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
class ImageTestCase(ImportTestCase):
    def test_upload_from_one_local_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_jp2_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/import-testing/test.jp2"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local jp2 image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local jp2 image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_ntf_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/import-testing/test.ntf"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local ntf image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local ntf image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_local_tiff_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local tiff image"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_with_one_tiff_and_one_basic_image(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        url_tiff = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        url_basic = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_basic = self.downloader(url_basic)
        path_tiff = self.downloader(url_tiff)
        assets = [
            {"content": path_basic, "external_id": "local basic image"},
            {"content": path_tiff, "external_id": "local tiff image"},
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters_sync = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local basic image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        expected_parameters_async = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        calls = [call(*expected_parameters_sync), call(*expected_parameters_async)]
        self.kili.graphql_client.execute.assert_has_calls(calls, any_order=True)

    def test_upload_from_several_batches(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        self.assert_upload_several_batches()

    def test_upload_from_one_hosted_image_authorized_while_local_forbidden(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        self.kili.kili_api_gateway.list_organizations = MagicMock(
            return_value=organization_generator(upload_local_data=False)
        )
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.kili, self.project_id, assets)
