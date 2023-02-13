from unittest.mock import MagicMock, call, patch

import pytest

from kili.graphql.operations.asset.queries import AssetQuery
from kili.graphql.operations.organization.queries import OrganizationQuery
from kili.graphql.operations.project.queries import ProjectQuery
from kili.queries.asset import QueriesAsset
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import UploadFromLocalDataForbiddenError
from tests.services.asset_import.base import ImportTestCase
from tests.services.asset_import.mocks import (
    mocked_organization_with_upload_from_local,
    mocked_project_input_type,
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("IMAGE"))
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
@patch.object(
    OrganizationQuery,
    "__call__",
    side_effect=mocked_organization_with_upload_from_local(upload_local_data=True),
)
class ImageTestCase(ImportTestCase):
    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_local_image(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        import_assets(self.auth, self.project_id, assets, verify=False)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_hosted_image(self, *_):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets, verify=False)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_local_tiff_image(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local tiff image"}]
        import_assets(self.auth, self.project_id, assets, verify=False)
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    @patch.object(AssetQuery, "count", return_value=1)  # 2 images are uploaded in different batches
    def test_upload_with_one_tiff_and_one_basic_image(self, *_):
        url_tiff = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        url_basic = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_basic = self.downloader(url_basic)
        path_tiff = self.downloader(url_tiff)
        assets = [
            {"content": path_basic, "external_id": "local basic image"},
            {"content": path_tiff, "external_id": "local tiff image"},
        ]
        import_assets(self.auth, self.project_id, assets, verify=False)
        expected_parameters_sync = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local basic image"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
            ["TODO"],
        )
        expected_parameters_async = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local tiff image"],
            ["unique_id"],
            ["{}"],
            "GEO_SATELLITE",
        )
        calls = [call(*expected_parameters_sync), call(*expected_parameters_async)]
        self.auth.client.execute.assert_has_calls(calls, any_order=True)

    @patch.object(AssetQuery, "count", return_value=5)
    def test_upload_from_several_batches(self, *_):
        self.assert_upload_several_batches()

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_hosted_image_authorized_while_local_forbidden(self, *_):
        OrganizationQuery.__call__.side_effect = mocked_organization_with_upload_from_local(
            upload_local_data=False
        )
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets, verify=False)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "local image"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.auth, self.project_id, assets, verify=False)
