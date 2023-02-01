from unittest.mock import MagicMock, patch

import pytest

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
@patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("PDF"))
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
class PDFTestCase(ImportTestCase):
    def test_upload_from_one_local_pdf(self, *_):
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local pdf file"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_pdf(self, *_):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_several_batches(self, *_):
        self.assert_upload_several_batches()

    def test_upload_from_one_hosted_pdf_authorized_while_local_forbidden(self, *_):
        OrganizationQuery.__call__.side_effect = mocked_organization_with_upload_from_local(
            upload_local_data=False
        )
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"], ["TODO"]
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.auth, self.project_id, assets)
