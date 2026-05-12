from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest

from kili.core.graphql.operations.asset.mutations import GQL_APPEND_MANY_ASSETS
from kili.domain.project import ProjectId
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import ImportValidationError
from tests.unit.services.asset_import.base import ImportTestCase
from tests.unit.services.asset_import.mocks import (
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
class TestContentType(ImportTestCase):
    def test_cannot_upload_an_image_to_video_project(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        # Extension check runs before MIME type check, so ImportValidationError is raised first
        with pytest.raises(ImportValidationError):
            import_assets(self.kili, ProjectId(self.project_id), assets, disable_tqdm=True)

    def test_cannot_import_files_not_found_to_an_image_project(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        path = "./doesnotexist.png"
        assets = [{"content": path, "external_id": "image"}]
        with pytest.raises(FileNotFoundError):
            import_assets(self.kili, ProjectId(self.project_id), assets, disable_tqdm=True)

    def test_cannot_upload_raw_text_to_pdf_project(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with pytest.raises(FileNotFoundError):
            import_assets(self.kili, ProjectId(self.project_id), assets, disable_tqdm=True)

    def test_return_the_ids_of_created_assets(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "TEXT"}
        assets = [{"content": "One"}, {"content": "Two"}, {"content": "Three"}]

        def graphql_execute_side_effect(*args, **kwargs):
            if args[0] == GQL_APPEND_MANY_ASSETS:
                return {"data": [{"id": "id1"}, {"id": "id2"}, {"id": "id3"}]}
            else:
                return MagicMock()

        self.kili.graphql_client.execute = MagicMock(side_effect=graphql_execute_side_effect)
        created_assets = import_assets(
            self.kili, ProjectId(self.project_id), assets, disable_tqdm=True
        )
        assert set(created_assets) == {"id1", "id2", "id3"}

    def test_generate_different_uuid4_external_ids_if_not_given(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "TEXT"}
        assets = [{"content": "One"}, {"content": "Two"}, {"content": "Three"}]
        self.kili.graphql_client.execute.reset_mock()
        import_assets(self.kili, ProjectId(self.project_id), assets, disable_tqdm=True)
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

    @patch("kili.services.asset_import.base.BaseBatchImporter.verify_batch_imported")
    def test_import_assets_verify(self, mocked_verify_batch_imported, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://hosted-data", "external_id": "externalid"}]

        import_assets(self.kili, ProjectId("project_id"), assets, verify=False)
        mocked_verify_batch_imported.assert_not_called()
        import_assets(self.kili, ProjectId("project_id"), assets, verify=True)
        mocked_verify_batch_imported.assert_called_once()


@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
class TestFileExtensionValidation(ImportTestCase):
    """Tests that the import service validates file extensions before uploading."""

    # --- IMAGE ---
    def test_image_project_rejects_video_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://example.com/clip.mp4", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.mp4"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_image_project_rejects_audio_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://example.com/sound.mp3", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.mp3"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_image_project_accepts_jpg_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://example.com/image.jpg", "external_id": "ok", "id": "uid"}]
        # Should not raise ImportValidationError
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_image_project_accepts_tif_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://example.com/geo.tif", "external_id": "ok", "id": "uid"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- VIDEO ---
    def test_video_project_rejects_image_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://example.com/photo.jpg", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.jpg"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_video_project_rejects_pdf_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://example.com/doc.pdf", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.pdf"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_video_project_accepts_mp4_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://example.com/vid.mp4", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_video_project_accepts_mkv_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://example.com/vid.mkv", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- AUDIO ---
    def test_audio_project_rejects_image_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "AUDIO"}
        assets = [{"content": "https://example.com/photo.jpg", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.jpg"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_audio_project_rejects_pdf_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "AUDIO"}
        assets = [{"content": "https://example.com/doc.pdf", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.pdf"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_audio_project_accepts_mp3_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "AUDIO"}
        assets = [{"content": "https://example.com/audio.mp3", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_audio_project_accepts_wav_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "AUDIO"}
        assets = [{"content": "https://example.com/audio.wav", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- PDF ---
    def test_pdf_project_rejects_image_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        assets = [{"content": "https://example.com/photo.jpg", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.jpg"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_pdf_project_rejects_video_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        assets = [{"content": "https://example.com/clip.mp4", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.mp4"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_pdf_project_accepts_pdf_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "PDF"}
        assets = [{"content": "https://example.com/doc.pdf", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- GEOSPATIAL ---
    def test_geospatial_project_rejects_image_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        assets = [{"content": "https://example.com/photo.jpg", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.jpg"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_geospatial_project_accepts_tif_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        assets = [{"content": "https://example.com/geo.tif", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_geospatial_project_accepts_jp2_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        assets = [{"content": "https://example.com/geo.jp2", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_geospatial_project_rejects_wrong_extension_in_multi_layer(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        assets = [
            {
                "multi_layer_content": [
                    {"path": "/local/layer.jpg", "name": "layer1"},
                ],
                "external_id": "wrong_multi_layer",
            }
        ]
        with pytest.raises(ImportValidationError, match=r"\.jpg"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_geospatial_project_accepts_correct_extension_in_multi_layer(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "GEOSPATIAL"}
        assets = [
            {
                "multi_layer_content": [
                    {"path": "/local/layer.tif", "name": "layer1"},
                    {"path": "/local/layer2.tiff", "name": "layer2"},
                ],
                "external_id": "ok_multi_layer",
            }
        ]
        # Should not raise ImportValidationError (may raise later on file access)
        with pytest.raises(Exception) as exc_info:
            import_assets(self.kili, ProjectId(self.project_id), assets)
        assert not isinstance(exc_info.value, ImportValidationError)

    # --- TEXT ---
    def test_text_project_rejects_video_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "TEXT"}
        assets = [{"content": "https://example.com/clip.mp4", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.mp4"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_text_project_accepts_txt_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "TEXT"}
        assets = [{"content": "https://example.com/file.txt", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_text_project_skips_validation_for_raw_text(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "TEXT"}
        assets = [{"content": "this is raw text with no extension", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- LLM_RLHF ---
    def test_llm_project_rejects_non_json_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        assets = [{"content": "https://example.com/data.txt", "external_id": "wrong"}]
        with pytest.raises(ImportValidationError, match=r"\.txt"):
            import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_llm_project_accepts_json_extension(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "LLM_RLHF"}
        assets = [{"content": "https://example.com/data.json", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    # --- no extension in URL skips validation ---
    def test_extensionless_url_skips_validation_for_image_project(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}
        assets = [{"content": "https://example.com/no-ext", "external_id": "ok", "id": "uid"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)

    def test_extensionless_url_skips_validation_for_video_project(self, *_):
        self.kili.kili_api_gateway.get_project.return_value = {"inputType": "VIDEO"}
        assets = [{"content": "https://hosted-data", "external_id": "ok"}]
        import_assets(self.kili, ProjectId(self.project_id), assets)
