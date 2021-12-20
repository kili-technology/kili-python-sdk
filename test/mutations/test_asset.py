"""
Test mutations with pytest
"""
import os
import json
import time
from unittest import TestCase
import uuid

import pytest
from kili.client import Kili
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
        path = os.path.join(self.directory, str(uuid.uuid4()))
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
