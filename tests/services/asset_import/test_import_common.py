from unittest.mock import patch
from uuid import UUID

from kili.graphql.operations.asset.queries import AssetQuery
from kili.graphql.operations.organization.queries import OrganizationQuery
from kili.graphql.operations.project.queries import ProjectQuery
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import MimeTypeError
from tests.services.asset_import.base import ImportTestCase
from tests.services.asset_import.mocks import (
    mocked_organization_with_upload_from_local,
    mocked_project_input_type,
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch.object(
    AssetQuery,
    "__call__",
    return_value=[],
)
@patch.object(
    OrganizationQuery,
    "__call__",
    side_effect=mocked_organization_with_upload_from_local(upload_local_data=True),
)
class TestContentType(ImportTestCase):
    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("VIDEO_LEGACY"))
    @patch.object(AssetQuery, "count", return_value=1)
    def test_cannot_upload_an_image_to_video_project(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        with self.assertRaises(MimeTypeError):
            import_assets(self.auth, self.project_id, assets, disable_tqdm=True, verify=False)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("IMAGE"))
    @patch.object(AssetQuery, "count", return_value=1)
    def test_cannot_import_files_not_found_to_an_image_project(self, *_):
        path = "./doesnotexist.png"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.auth, self.project_id, assets, disable_tqdm=True, verify=False)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("PDF"))
    @patch.object(AssetQuery, "count", return_value=1)
    def test_cannot_upload_raw_text_to_pdf_project(self, *_):
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.auth, self.project_id, assets, disable_tqdm=True, verify=False)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("TEXT"))
    @patch.object(AssetQuery, "count", return_value=3)
    def test_generate_different_uuid4_external_ids_if_not_given(self, *_):
        assets = [{"content": "One"}, {"content": "Two"}, {"content": "Three"}]
        self.auth.client.execute.reset_mock()
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True, verify=False)
        self.auth.client.execute.assert_called_once()
        call_args = self.auth.client.execute.call_args[0]
        external_id_array_call = call_args[1]["data"]["externalIDArray"]
        external_ids_are_uniques = len(set(external_id_array_call)) == len(external_id_array_call)
        try:
            for external_id in external_id_array_call:
                _ = UUID(external_id, version=4)
            external_ids_are_uuid4 = True
        except ValueError:
            external_ids_are_uuid4 = False
        assert external_ids_are_uuid4
        assert external_ids_are_uniques

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("IMAGE"))
    @patch.object(AssetQuery, "count", return_value=1)
    @patch("kili.services.asset_import.base.BaseBatchImporter.verify_batch_imported")
    def test_import_assets_verify(self, mocked_verify_batch_imported, *_):
        assets = [{"content": "https://hosted-data", "external_id": "externalid"}]

        import_assets(self.auth, "project_id", assets, verify=False)
        mocked_verify_batch_imported.assert_not_called()
        import_assets(self.auth, "project_id", assets, verify=True)
        mocked_verify_batch_imported.assert_called_once()
