import json
from unittest.mock import MagicMock, patch

import pytest

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.organization.queries import OrganizationQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.entrypoints.queries.asset import QueriesAsset
from kili.services.asset_import import import_assets
from kili.services.asset_import.exceptions import UploadFromLocalDataForbiddenError
from tests.services.asset_import.base import ImportTestCase
from tests.services.asset_import.mocks import (
    mocked_organization_with_upload_from_local,
    mocked_project_input_type,
    mocked_request_signed_urls,
    mocked_unique_id,
    mocked_upload_data_via_rest,
)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("VIDEO"))
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
@patch.object(
    OrganizationQuery,
    "__call__",
    side_effect=mocked_organization_with_upload_from_local(upload_local_data=True),
)
@patch.object(AssetQuery, "count", return_value=1)
class VideoTestCase(ImportTestCase):
    def test_upload_from_one_local_video_file_to_native(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local video file to native"}]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            ["https://signed_url?id=id"],
            ["local video file to native"],
            ["unique_id"],
            [False],
            [""],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_video_file_to_native(self, *_):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"],
            ["hosted file"],
            ["unique_id"],
            [False],
            [""],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_from_one_hosted_video_authorized_while_local_forbidden(self, *_):
        OrganizationQuery.__call__.side_effect = mocked_organization_with_upload_from_local(
            upload_local_data=False
        )
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"],
            ["hosted file"],
            ["unique_id"],
            [False],
            [""],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        path = self.downloader(url)
        assets = [{"content": path, "external_id": "local video file to native"}]
        with pytest.raises(UploadFromLocalDataForbiddenError):
            import_assets(self.auth, self.project_id, assets, disable_tqdm=True)

    def test_upload_one_local_video_to_frames(self, *_):
        url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        path = self.downloader(url)
        assets = [
            {
                "content": path,
                "external_id": "local video to frames",
                "id": "unique_id",
                "json_metadata": {
                    "processingParameters": {
                        "shouldUseNativeVideo": False,
                    }
                },
            }
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldUseNativeVideo": False,
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                }
            }
        )
        expected_parameters = self.get_expected_async_call(
            ["https://signed_url?id=id"],
            ["local video to frames"],
            ["unique_id"],
            [expected_json_metadata],
            "VIDEO",
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_one_hosted_video_to_frames(self, *_):
        assets = [
            {
                "content": "https://hosted-data",
                "external_id": "changing fps",
                "id": "unique_id",
                "json_metadata": {
                    "processingParameters": {
                        "shouldUseNativeVideo": False,
                    }
                },
            }
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)

        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldUseNativeVideo": False,
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                }
            }
        )
        expected_parameters = self.get_expected_async_call(
            ["https://hosted-data"],
            ["changing fps"],
            ["unique_id"],
            [expected_json_metadata],
            "VIDEO",
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_one_video_from_local_frames(self, *_):
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
                "id": "unique_id",
            }
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            [""],
            ["from local frames"],
            ["unique_id"],
            [False],
            ["https://signed_url?id=id"],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_one_video_from_hosted_frames(self, *_):
        url_frame1 = "https://frame1"
        url_frame2 = "https://frame2"
        url_frame3 = "https://frame3"
        assets = [
            {
                "external_id": "from hosted frames",
                "json_content": [url_frame1, url_frame2, url_frame3],
                "id": "unique_id",
            }
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            [""],
            ["from hosted frames"],
            ["unique_id"],
            [False],
            ["https://signed_url?id=id"],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_upload_frames_call_from_label_import(self, *_):
        url_frame1 = "https://frame1"
        url_frame2 = "https://frame2"
        url_frame3 = "https://frame3"
        assets = [
            {
                "content": "https://reading_signed_url_content",
                "external_id": "from label-import",
                "id": "unique_id",
                "json_content": [url_frame1, url_frame2, url_frame3],
            }
        ]
        import_assets(self.auth, self.project_id, assets)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": False,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": False,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            ["https://reading_signed_url_content"],
            ["from label-import"],
            ["unique_id"],
            [False],
            ["https://signed_url?id=id"],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)

    def test_import_one_video_with_metadata(self, *_):
        assets = [
            {
                "content": "https://hosted-data",
                "external_id": "with metadata",
                "id": "unique_id",
                "json_metadata": {"fromBucket": True, "score": 10},
            }
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
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
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"],
            ["with metadata"],
            ["unique_id"],
            [False],
            [""],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)


@patch("kili.utils.bucket.request_signed_urls", mocked_request_signed_urls)
@patch("kili.utils.bucket.upload_data_via_rest", mocked_upload_data_via_rest)
@patch("kili.utils.bucket.generate_unique_id", mocked_unique_id)
@patch.object(ProjectQuery, "__call__", side_effect=mocked_project_input_type("VIDEO_LEGACY"))
@patch.object(
    QueriesAsset,
    "assets",
    MagicMock(return_value=[]),
)
@patch.object(AssetQuery, "count", return_value=1)
class VideoLegacyTestCase(ImportTestCase):
    def test_upload_from_one_hosted_video_file_to_video_legacy_project(self, *_):
        assets = [
            {"content": "https://hosted-data", "external_id": "hosted file", "id": "unique_id"}
        ]
        import_assets(self.auth, self.project_id, assets, disable_tqdm=True)
        expected_json_metadata = json.dumps(
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "framesPlayedPerSecond": 30,
                    "shouldUseNativeVideo": True,
                }
            }
        )
        expected_parameters = self.get_expected_sync_call(
            ["https://hosted-data"],
            ["hosted file"],
            ["unique_id"],
            [False],
            [""],
            [expected_json_metadata],
            ["TODO"],
        )
        self.auth.client.execute.assert_called_with(*expected_parameters)
