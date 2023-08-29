from unittest.mock import MagicMock, patch
from uuid import UUID

from kili.core.graphql.operations.asset.mutations import GQL_APPEND_MANY_ASSETS
from kili.core.graphql.operations.organization.queries import OrganizationQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.gateways.kili_api_gateway.asset import AssetOperationMixin
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import MimeTypeError
from tests.unit.services.asset_import.base import ImportTestCase
from tests.unit.services.asset_import.mocks import (
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
    OrganizationQuery,
    "__call__",
    side_effect=mocked_organization_with_upload_from_local(upload_local_data=True),
)
class TestContentType(ImportTestCase):
    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("VIDEO_LEGACY"))
    def test_cannot_upload_an_image_to_video_project(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        with self.assertRaises(MimeTypeError):
            import_assets(self.kili, self.project_id, assets, disable_tqdm=True)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("IMAGE"))
    def test_cannot_import_files_not_found_to_an_image_project(self, *_):
        path = "./doesnotexist.png"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.kili, self.project_id, assets, disable_tqdm=True)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("PDF"))
    def test_cannot_upload_raw_text_to_pdf_project(self, *_):
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.kili, self.project_id, assets, disable_tqdm=True)

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("TEXT"))
    def test_return_the_ids_of_created_assets(self, *_):
        assets = [{"content": "One"}, {"content": "Two"}, {"content": "Three"}]

        def graphql_execute_side_effect(*args, **kwargs):
            if args[0] == GQL_APPEND_MANY_ASSETS:
                return {"data": [{"id": "id1"}, {"id": "id2"}, {"id": "id3"}]}
            else:
                return MagicMock()

        self.kili.graphql_client.execute = MagicMock(side_effect=graphql_execute_side_effect)
        created_assets = import_assets(self.kili, self.project_id, assets, disable_tqdm=True)
        assert set(created_assets) == {"id1", "id2", "id3"}

    @patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("TEXT"))
    def test_generate_different_uuid4_external_ids_if_not_given(self, *_):
        assets = [{"content": "One"}, {"content": "Two"}, {"content": "Three"}]
        self.kili.graphql_client.execute.reset_mock()
        import_assets(self.kili, self.project_id, assets, disable_tqdm=True)
        self.kili.graphql_client.execute.assert_called_once()
        call_args = self.kili.graphql_client.execute.call_args[0]
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
    @patch("kili.services.asset_import.base.BaseBatchImporter.verify_batch_imported")
    def test_import_assets_verify(self, mocked_verify_batch_imported, *_):
        assets = [{"content": "https://hosted-data", "external_id": "externalid"}]

        import_assets(self.kili, "project_id", assets, verify=False)
        mocked_verify_batch_imported.assert_not_called()
        import_assets(self.kili, "project_id", assets, verify=True)
        mocked_verify_batch_imported.assert_called_once()
