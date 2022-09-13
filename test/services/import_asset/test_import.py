import shutil
import tempfile
from test.utils import LocalDownloader
from unittest import TestCase

from kili.services.import_asset import import_assets


class TestContentType(TestCase):
    def setUp(self):
        self.project_id = "project_id"
        self.auth = None
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cannot_upload_an_image_to_video_project(self):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        path_image = self.downloader(url)
        assets = [{"content": path_image, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, "VIDEO", self.project_id, assets)

    def test_cannot_files_not_found_to_an_image_project(self):
        path = "./doesnotexist.pdf"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, "PDF", self.project_id, assets)

    def test_cannot_upload_raw_text_to_pdf_project(self):
        path = "Hello world"
        assets = [{"content": path, "external_id": "image"}]
        with self.assertRaises(ValueError):
            import_assets(self.auth, "PDF", self.project_id, assets)
