import shutil
import tempfile
from test.services.asset_import.mocks import mocked_request_signed_urls
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kili.queries.project import QueriesProject
from kili.services.asset_import import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
class TestContentType(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.auth = None
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)
        self.auth = None

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "VIDEO"}]),
    )
    def test_cannot_upload_an_image_to_video_project(self):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, self.project_id, assets)

    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "IMAGE"}]),
    )
    def test_cannot_import_files_not_found_to_an_image_project(self):
        path = "./doesnotexist.pdf"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, self.project_id, assets)

    @patch.object(
        QueriesProject,
        "projects",
        MagicMock(return_value=[{"inputType": "PDF"}]),
    )
    def test_cannot_upload_raw_text_to_pdf_project(self):
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, self.project_id, assets)
