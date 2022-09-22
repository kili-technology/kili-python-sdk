from test.services.asset_import.base import ImportTestCase
from test.services.asset_import.mocks import mocked_request_signed_urls
from unittest.mock import MagicMock, patch

from kili.queries.asset import QueriesAsset
from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import MimeTypeError


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
class TestContentType(ImportTestCase):
    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "VIDEO"}]),
    )
    def test_cannot_upload_an_image_to_video_project(self):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        with self.assertRaises(MimeTypeError):
            import_assets(self.auth, self.project_id, assets)

    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "IMAGE"}]),
    )
    def test_cannot_import_files_not_found_to_an_image_project(self):
        path = "./doesnotexist.png"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.auth, self.project_id, assets)

    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "PDF"}]),
    )
    def test_cannot_upload_raw_text_to_pdf_project(self):
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(FileNotFoundError):
            import_assets(self.auth, self.project_id, assets)
