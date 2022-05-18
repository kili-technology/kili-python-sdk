"""
Test mutations with pytest
"""
import os
import json
import time
import shutil
import tempfile
from unittest import TestCase
import unittest
import uuid

import pytest
from kili.client import Kili
from kili.mutations.asset.helpers import get_file_mimetype, process_append_many_to_dataset_parameters, process_content
from kili.mutations.asset.queries import GQL_APPEND_MANY_FRAMES_TO_DATASET
import requests

api_key = os.getenv('KILI_USER_API_KEY')
api_endpoint = os.getenv('KILI_API_ENDPOINT')
kili = Kili(api_key=api_key, api_endpoint=api_endpoint)


tester = TestCase()

@pytest.fixture
def create_video_project():
    """
    Create a video project
    """
    with open('./test/mutations/interface.json', 'r') as file:
        interface = json.load(file)
    project = kili.create_project(
        input_type='FRAME', json_interface=interface, title='Test project | video import')
    return project['id']

class LocalDownloader():

    def __init__(self, directory):
        self.directory = directory

    def __call__(self, url):
        content = requests.get(url)
        name = os.path.basename(url)
        path = os.path.join(self.directory, f'{str(uuid.uuid4())}-{name}')
        with open(path, 'wb') as file:
            file.write(content.content)
        return path


TIMEOUT = 10
RETRY = 1
BASE_TEST_CASES = [
    {
        'case': 'uploading a video with a url',
        'content': ['https://storage.googleapis.com/label-public-staging/presales/industry_small.mp4'],
        'expected_processing_parameters': {
            'shouldKeepNativeFrameRate': True,
            'framesPlayedPerSecond': 25,
            'shouldUseNativeVideo': True
        }
    },
    {
        'case': 'uploading a video as a list of image urls',
        'json_content': [["https://storage.googleapis.com/label-public-staging/video1/video1-img000001.jpg",
                            "https://storage.googleapis.com/label-public-staging/video1/video1-img000002.jpg"]],
        'expected_processing_parameters': {
            'shouldKeepNativeFrameRate': False,
            'framesPlayedPerSecond': 30,
            'shouldUseNativeVideo': False
        }
    },
    {
        'case': 'uploading a video into frames from url',
        'content': ['https://storage.googleapis.com/label-public-staging/presales/industry_small.mp4'],
        'expected_processing_parameters': {
            'shouldKeepNativeFrameRate': True,
            'shouldUseNativeVideo': False,
            'framesPlayedPerSecond': 25,
        },
        'json_metadata': [{
            'processingParameters': {
                'shouldKeepNativeFrameRate': True,
                'shouldUseNativeVideo': False,
            }
        }],
    },
    
]
CUSTOM_VALUE_CASES = [
    {
        'case': 'uploading a video with a url',
        'content': ['https://storage.googleapis.com/label-public-staging/presales/industry_small.mp4'],
        'expected_processing_parameters': {
            'shouldKeepNativeFrameRate': False,
            'framesPlayedPerSecond': 40,
            'shouldUseNativeVideo': True
        },
        'json_metadata': [{
            'processingParameters': {
                'shouldKeepNativeFrameRate': False,
                'framesPlayedPerSecond': 40,
            }
        }]
    },
]
TEST_CASES = BASE_TEST_CASES
TEST_CASES.extend([{**x, 'local': True} for x in BASE_TEST_CASES])
TEST_CASES.extend(CUSTOM_VALUE_CASES)


def test_upload_video(create_video_project, tmpdir):
    """
    Test upload of video in different ways
    """
    project_id = create_video_project
    assert project_id != '', 'Project not successfully created'

    downloader = LocalDownloader(tmpdir)

    for i, test_case in enumerate(TEST_CASES):
        external_id = f'video_case_{i+1}'
        content = test_case.get('content', None)
        expected_parameters = test_case.get(
            'expected_processing_parameters', {})
        json_metadata = test_case.get('json_metadata', None)
        json_content = test_case.get('json_content', None)
        local = test_case.get('local', False)
        case = test_case.get('case', 'Unknown case') + f' | {"local" if local else "cloud"}'
        print('case', case)
        if local:
            if content is not None:
                content = list(map(downloader, content))
            else:
                json_content = list(map(lambda jc: [downloader(x) for x in jc], json_content))


        kili.append_many_to_dataset(
            project_id=project_id,
            content_array=content,
            json_metadata_array=json_metadata,
            json_content_array=json_content,
            external_id_array=[external_id]
        )

        tstart = time.time()
        n_assets = kili.count_assets(project_id=project_id)
        while not n_assets == i+1 and time.time() - tstart < TIMEOUT:
            time.sleep(RETRY)
            n_assets = kili.count_assets(project_id=project_id)
        assert n_assets == i+1, 'Asset upload failed'

        asset_uploaded = kili.assets(
            project_id=project_id, external_id_contains=[external_id])
        processed_parameters = asset_uploaded[0]['jsonMetadata']['processingParameters']
        tester.assertDictEqual(expected_parameters, processed_parameters), f'{case}, got {processed_parameters}, expected {expected_parameters}'

class TestMimeType():
    """
    Tests if the mime type is the correct one
    """

    def should_have_right_mimetype(self, content_array, json_content_array, expected_mimetype):
        mimetype = get_file_mimetype(content_array, json_content_array)
        assert mimetype == expected_mimetype, f'Bad mimetype {mimetype}'

    def test_contents_empty(self):
        content_array = None
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, None)

    def test_mimetype_url(self, tmpdir):
        url = 'https://storage.googleapis.com/label-public-staging/car/car_1.jpg'
        content_array = [url]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, None)

    def test_mimetype_image(self, tmpdir):
        url = 'https://storage.googleapis.com/label-public-staging/car/car_1.jpg'
        downloader = LocalDownloader(tmpdir)
        path = downloader(url)
        content_array = [path]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, 'image/jpeg')

    def test_mimetype_geotiff(self, tmpdir):
        url = 'https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif'
        downloader = LocalDownloader(tmpdir)
        path = downloader(url)
        content_array = [path]
        json_content_array = None
        self.should_have_right_mimetype(content_array, json_content_array, 'image/tiff')
    
    def test_cannot_upload_mp4_to_image_project(self):
        path = './test.mp4'
        content_array = [path]
        json_content_array = None
        processed_content = process_content('IMAGE', content_array, json_content_array)
        assert(processed_content==[None])

    def test_cannot_upload_png_to_frame_project(self):
        path = './test.png'
        content_array = [path]
        json_content_array = None
        processed_content = process_content('FRAME', content_array, json_content_array)
        assert(processed_content==[None])

    def test_cannot_upload_text_to_pdf_project(self):
        path = 'Hello world'
        content_array = [path]
        json_content_array = None
        processed_content = process_content('PDF', content_array, json_content_array)
        assert(processed_content==[None])

    @pytest.mark.xfail(raises=FileNotFoundError)
    def test_can_upload_png_to_image_project(self):
        path = './test.png'
        content_array = [path]
        json_content_array = None
        process_content('IMAGE', content_array, json_content_array)


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

    def test_geotiff_upload(self):
        url = 'https://storage.googleapis.com/label-public-staging/geotiffs/bogota.tif'
        downloader = LocalDownloader(self.test_dir)
        path = downloader(url)
        input_type = 'IMAGE'
        content_array = [path]
        external_id_array = ['bogota']
        is_honeypot_array = None
        status_array = None
        json_content_array = None
        json_metadata_array = None
        payload, request = process_append_many_to_dataset_parameters(
            input_type,
            content_array,
            external_id_array,
            is_honeypot_array,
            status_array,
            json_content_array,
            json_metadata_array,
        )
        payload_content = payload['contentArray']
        del payload['contentArray']
        expected_payload = {'externalIDArray': external_id_array,
                        'jsonMetadataArray': ['{}'],
                        'uploadType': 'GEO_SATELLITE'}
        expected_request = GQL_APPEND_MANY_FRAMES_TO_DATASET
        assert expected_request == request, 'Requests do not match'
        assert payload_content[0].startswith('data:image/tiff;base64,SUkqAAgABABre')
        self.assertEqual(expected_payload, payload, 'Payloads do not match')