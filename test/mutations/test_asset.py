"""
Test mutations with pytest
"""
import os
import shutil
import tempfile
import unittest
import uuid

import pytest
import requests

from kili.mutations.asset.helpers import (
    get_file_mimetype,
    process_append_many_to_dataset_parameters,
    process_content,
)
from kili.mutations.asset.queries import GQL_APPEND_MANY_FRAMES_TO_DATASET


class LocalDownloader:
    def __init__(self, directory):
        self.directory = directory

    def __call__(self, url):
        content = requests.get(url)
        name = os.path.basename(url)
        path = os.path.join(self.directory, f"{str(uuid.uuid4())}-{name}")
        with open(path, "wb") as file:
            file.write(content.content)
        return path


class TestMimeType:
    """
    Tests if the mime type is the correct one
    """

    def should_have_right_mimetype(self, content_array, json_content_array, expected_mimetype):
        mimetype = get_file_mimetype(content_array, json_content_array)
        assert mimetype == expected_mimetype, f"Bad mimetype {mimetype}"

    def test_contents_empty(self):
        content_array = None
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, None)

    def test_mimetype_url(self, tmpdir):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        content_array = [url]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, None)

    def test_mimetype_image(self, tmpdir):
        url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
        downloader = LocalDownloader(tmpdir)
        path = downloader(url)
        content_array = [path]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, "image/jpeg")

    def test_mimetype_geotiff(self, tmpdir):
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        downloader = LocalDownloader(tmpdir)
        path = downloader(url)
        content_array = [path]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, "image/tiff")

    def test_cannot_upload_mp4_to_image_project(self):
        path = "./test.mp4"
        content_array = [path]
        json_content_array = None
        processed_content = process_content("IMAGE", content_array, json_content_array)
        assert processed_content == [None]

    def test_cannot_upload_png_to_frame_project(self):
        path = "./test.png"
        content_array = [path]
        json_content_array = None
        processed_content = process_content("VIDEO", content_array, json_content_array)
        assert processed_content == [None]

    def test_cannot_upload_text_to_pdf_project(self):
        path = "Hello world"
        content_array = [path]
        json_content_array = None
        processed_content = process_content("PDF", content_array, json_content_array)
        assert processed_content == [None]

    def test_can_upload_png_to_image_project(self):
        with pytest.raises(FileNotFoundError):
            path = "./test.png"
            content_array = [path]
            json_content_array = None
            process_content("IMAGE", content_array, json_content_array)


class TestUploadTiff(unittest.TestCase):
    """
    Test functions for uploading geotiff
    """

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_geotiff_upload_properties(self):
        url = "https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif"
        downloader = LocalDownloader(self.test_dir)
        path = downloader(url)
        input_type = "IMAGE"
        content_array = [path]
        external_id_array = ["bogota"]
        is_honeypot_array = None
        status_array = None
        json_content_array = None
        json_metadata_array = None
        properties, upload_type, request = process_append_many_to_dataset_parameters(
            input_type,
            content_array,
            external_id_array,
            is_honeypot_array,
            status_array,
            json_content_array,
            json_metadata_array,
        )
        assert properties["json_metadata_array"] == ["{}"]
        assert properties["content_array"][0].startswith("data:image/tiff;base64,SUkqAAgABABre")
        assert properties["external_id_array"] == ["bogota"]
        assert upload_type == "GEO_SATELLITE", "uploadType do not match"
        assert request == GQL_APPEND_MANY_FRAMES_TO_DATASET, "Requests do not match"
