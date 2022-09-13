import json
import shutil
import tempfile
from test.services.import_asset.mocks import (
    mocked__mutate_from_paginated_call,
    mocked_request_signed_urls,
    mocked_upload_data_via_rest,
)
from test.utils import LocalDownloader
from unittest import TestCase
from unittest.mock import ANY, patch

from kili.graphQL.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.helpers import encode_base64
from kili.services.import_asset import import_assets


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.pagination._mutate_from_paginated_call", mocked__mutate_from_paginated_call)
class VideoTestCase(TestCase):
    def setUp(self):
        self.input_type = "VIDEO"
        self.project_id = "video_project_id"
        self.auth = None
        self.test_dir = tempfile.mkdtemp()
        self.downloader = LocalDownloader(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upload_from_one_local_video_file_to_native(self):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local video file to native"}]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://signed_url"],
                "external_id_array": ["local video file to native"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_from_one_hosted_video_file_to_native(
        self,
    ):
        assets = [{"content": "https://hosted-data", "external_id": "hosted file"}]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://hosted-data"],
                "external_id_array": ["hosted file"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_one_local_video_to_frames(self):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        path = self.downloader(url)
        assets = [
            {
                "content": path,
                "external_id": "local video to frames",
                "json_metadata": {
                    "processingParameters": {
                        "shouldUseNativeVideo": False,
                    }
                },
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldUseNativeVideo": False,
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                }
            }
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://signed_url"],
                "external_id_array": ["local video to frames"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_FRAMES_TO_DATASET,
        )

    def test_upload_one_hosted_video_to_frames(self):
        assets = [
            {
                "content": "https://hosted-data",
                "external_id": "changing fps",
                "json_metadata": {
                    "processingParameters": {
                        "shouldUseNativeVideo": False,
                    }
                },
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldUseNativeVideo": False,
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                }
            }
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://hosted-data"],
                "external_id_array": ["changing fps"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_FRAMES_TO_DATASET,
        )

    def test_upload_one_video_from_local_frames(self):
        hosted_frame_folder = (
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/frames/"
        )
        path_frame1 = self.downloader(hosted_frame_folder + "video2-img000001.jpeg")
        path_frame2 = self.downloader(hosted_frame_folder + "video2-img000010.jpeg")
        path_frame3 = self.downloader(hosted_frame_folder + "video2-img000020.jpeg")
        assets = [
            {
                "external_id": "from local frames",
                "json_content": [path_frame1, path_frame2, path_frame3],
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_called_json_content = json.dumps(
            dict(
                zip(
                    [0, 1, 2],
                    [
                        encode_base64(frame_path)
                        for frame_path in [path_frame1, path_frame2, path_frame3]
                    ],
                )
            )
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": [""],
                "external_id_array": ["from local frames"],
                "is_honeypot_array": [False],
                "json_content_array": [expected_called_json_content],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_one_video_from_hosted_frames(self):
        url_frame1 = "https://frame1"
        url_frame2 = "https://frame2"
        url_frame3 = "https://frame3"
        assets = [
            {
                "external_id": "from hosted frames",
                "json_content": [url_frame1, url_frame2, url_frame3],
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_called_json_content = json.dumps(
            dict(
                zip(
                    [0, 1, 2],
                    [url_frame1, url_frame2, url_frame3],
                )
            )
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": [""],
                "external_id_array": ["from hosted frames"],
                "is_honeypot_array": [False],
                "json_content_array": [expected_called_json_content],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_upload_frames_call_from_label_import(self):
        url_frame1 = "https://frame1"
        url_frame2 = "https://frame2"
        url_frame3 = "https://frame3"
        assets = [
            {
                "content": "https://reading_signed_url_content",
                "external_id": "from label-import",
                "json_content": [url_frame1, url_frame2, url_frame3],
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_called_json_content = json.dumps(
            dict(
                zip(
                    [0, 1, 2],
                    [url_frame1, url_frame2, url_frame3],
                )
            )
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://reading_signed_url_content"],
                "external_id_array": ["from label-import"],
                "is_honeypot_array": [False],
                "json_content_array": [expected_called_json_content],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )

    def test_import_one_video_with_metadata(self):
        assets = [
            {
                "content": "https://hosted-data",
                "external_id": "with metadata",
                "json_metadata": {"fromBucket": True, "score": 10},
            }
        ]
        import_assets(self.auth, self.input_type, self.project_id, assets)
        expected_called_json_metadata = json.dumps(
            {
                "fromBucket": True,
                "score": 10,
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                },
            }
        )
        mocked__mutate_from_paginated_call.assert_called_with(
            ANY,
            {
                "content_array": ["https://hosted-data"],
                "external_id_array": ["with metadata"],
                "is_honeypot_array": [False],
                "json_content_array": [""],
                "json_metadata_array": [expected_called_json_metadata],
                "status_array": ["TODO"],
            },
            ANY,
            GQL_APPEND_MANY_TO_DATASET,
        )
