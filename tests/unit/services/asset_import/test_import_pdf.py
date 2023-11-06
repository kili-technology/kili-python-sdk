from unittest.mock import MagicMock, patch

import pytest

from kili.adapters.kili_api_gateway.asset.operations_mixin import AssetOperationMixin
from kili.adapters.kili_api_gateway.organization.operations_mixin import (
    OrganizationOperationMixin,
)
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
@patch.object(AssetOperationMixin, "list_assets", MagicMock(return_value=[]))
@patch.object(
    OrganizationOperationMixin,
    "list_organizations",
    side_effect=organization_generator(upload_local_data=True),
)
class PDFTestCase(ImportTestCase):
    def test_upload_from_one_local_pdf(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local pdf file"],
            ["unique_id"],
            [False],
            [""],
            ["{}"],
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_pdf(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.kili, self.project_id, assets)
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"], ["hosted file"], ["unique_id"], [False], [""], ["{}"]
        )
        self.kili.graphql_client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_several_batches(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        self.assert_upload_several_batches()

    def test_upload_from_one_hosted_pdf_authorized_while_local_forbidden(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
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
        url = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/pdfs/sample.pdf"
        )
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local pdf file"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.kili, self.project_id, assets)
