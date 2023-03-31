from unittest.mock import MagicMock, patch

import pytest

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.organization.queries import OrganizationQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.queries.asset import QueriesAsset
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import UploadFromLocalDataForbiddenError
from tests.services.asset_import.base import ImportTestCase
from tests.services.asset_import.mocks import (
    mocked_organization_with_upload_from_local,
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch.object(ProjectQuery, "__call__", side_effect=lambda *args: [{"inputType": "TEXT"}])
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
class TextTestCase(ImportTestCase):
    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_local_text_file(self, *_):
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

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_hosted_text_file(self, *_):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_raw_text(self, *_):
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

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_rich_text(self, *_):
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

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_several_batches(self, *_):
        self.assert_upload_several_batches()

    @patch.object(AssetQuery, "count", return_value=1)
    def test_upload_from_one_hosted_text_authorized_while_local_forbidden(self, *_):
        OrganizationQuery.__call__.side_effect = mocked_organization_with_upload_from_local(
            upload_local_data=False
        )
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/texts/test_text_file.txt"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local text file"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.auth, self.project_id, assets)

        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)
