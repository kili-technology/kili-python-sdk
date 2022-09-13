"""
Test mutations with pytest
"""
import os
import shutil
import tempfile
import unittest
import uuid
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from kili.helpers import check_file_mime_type
from kili.mutations.asset.helpers import (
    get_file_mimetype,
    process_and_store_content,
    process_append_many_to_dataset_parameters,
    upload_content,
)
from kili.mutations.asset.queries import GQL_APPEND_MANY_FRAMES_TO_DATASET
from kili.queries import project


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

    project_id = "project_id"

    def should_have_right_mimetype(self, content_array, json_content_array, expected_mimetype):
        mimetype = get_file_mimetype(content_array, json_content_array)
        assert mimetype == expected_mimetype, f"Bad mimetype {mimetype}"

    def test_contents_empty(self):
        content_array = None
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, None)

    def test_mimetype_url(self):
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
        with pytest.raises(ValueError):
            check_file_mime_type(path, "IMAGE")

    def test_cannot_upload_png_to_frame_project(self):
        path = "./test.png"
        with pytest.raises(ValueError):
            check_file_mime_type(path, "VIDEO")

    def test_cannot_upload_text_to_pdf_project(self):
        path = "Hello world"
        content_array = [path]
        auth = Mock()
        project_id = "project_id"
        with pytest.raises(ValueError):
            upload_content(content_array, "PDF", auth, project_id)

    def test_can_upload_png_to_image_project(self):
        path = "./test.png"
        assert check_file_mime_type(path, "IMAGE")


def mocked_request_signed_urls(_a, _b, size):
    return ["upload_signed_url"] * size


def mocked_upload_data_via_rest(signed_urls, *_):
    return [signed_urls]


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

    @patch(
        "kili.mutations.asset.helpers.request_signed_urls",
        MagicMock(side_effect=mocked_request_signed_urls),
    )
    @patch(
        "kili.mutations.asset.helpers.upload_data_via_rest",
        MagicMock(side_effect=mocked_upload_data_via_rest),
    )
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
        project_id = "projectr_id"
        auth = None
        (
            properties,
            upload_type,
            request,
            is_uploading_local_file,
        ) = process_append_many_to_dataset_parameters(
            auth,
            input_type,
            content_array,
            external_id_array,
            is_honeypot_array,
            status_array,
            json_content_array,
            json_metadata_array,
            project_id,
        )
        assert properties["json_metadata_array"] == ["{}"]
        assert properties["content_array"][0] == ["upload_signed_url"]
        assert (
            is_uploading_local_file == True
        ), "did not detect that it was uploading from a local file"
        assert properties["external_id_array"] == ["bogota"]
        assert upload_type == "GEO_SATELLITE", "uploadType do not match"
        assert request == GQL_APPEND_MANY_FRAMES_TO_DATASET, "Requests do not match"
