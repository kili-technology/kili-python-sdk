"""
Unit tests for helpers.py of .assets
"""

import os
from pathlib import Path

import pytest

from kili.queries.asset.helpers import MediaDownloader
from kili.utils.tempfile import TemporaryDirectory


@pytest.mark.parametrize(
    "input_asset,expected_filename",
    [
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4",
                "jsonContent": "",
                "externalId": "vid 1",
                "project": {"inputType": "VIDEO"},
            },
            "vid 1.mp4",
        ),
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/car/car_2.jpg",
                "jsonContent": "",
                "externalId": "car_2",
                "project": {"inputType": "IMAGE"},
            },
            "car_2.jpg",
        ),
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "jsonContent": "",
                "externalId": "car_1",
                "project": {"inputType": "IMAGE"},
            },
            "car_1.jpg",
        ),
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/recipes/inference/black_car.jpg",
                "jsonContent": "",
                "externalId": "black_car",
                "project": {"inputType": "IMAGE"},
            },
            "black_car.jpg",
        ),
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "jsonContent": "",
                "externalId": "car_1.jpg",
                "project": {"inputType": "IMAGE"},
            },
            "car_1.jpg",
        ),
        (
            {
                "content": "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4",
                "jsonContent": "",
                "externalId": "short_video.mp4",
                "project": {"inputType": "VIDEO"},
            },
            "short_video.mp4",
        ),
    ],
)
def test_download_single_asset_mixed(input_asset, expected_filename):
    """Tests download_single_asset with asset["content"]"""
    with TemporaryDirectory() as tmp_dir:
        output_asset = MediaDownloader(
            tmp_dir, "", False, input_asset["project"]["inputType"]
        ).download_single_asset(input_asset)

        assert output_asset["content"] == os.path.join(str(tmp_dir.resolve()), expected_filename)
        assert Path(output_asset["content"]).is_file()
        assert output_asset["jsonContent"] == input_asset["jsonContent"] == ""
        assert output_asset["externalId"] == input_asset["externalId"]


@pytest.mark.parametrize(
    "input_asset",
    [
        (
            {
                "content": "",
                "jsonContent": "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2_video2-json-content.json",
                "externalId": "vid 2",
                "project": {"inputType": "VIDEO"},
            }
        ),
        (
            {
                "content": "",
                "jsonContent": "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2_video2-json-content.json",
                "externalId": "vid 2.mp4",
                "project": {"inputType": "VIDEO"},
            }
        ),
    ],
)
def test_download_single_asset_jsoncontent(input_asset):
    """Tests with asset["jsonContent"] and extension in externalid"""
    with TemporaryDirectory() as tmp_dir:
        output_asset = MediaDownloader(
            tmp_dir, "", False, input_asset["project"]["inputType"]
        ).download_single_asset(input_asset)

        assert output_asset["content"] == input_asset["content"] == ""
        assert isinstance(output_asset["jsonContent"], list)
        assert len(output_asset["jsonContent"]) == 130
        frames = [
            filename
            for filename in os.listdir(tmp_dir)
            if filename.startswith(f'{input_asset["externalId"]}_')
        ]
        assert len(frames) == 130
        assert sorted(frames)[0] == f'{input_asset["externalId"]}_001.jpg'
        assert output_asset["externalId"] == input_asset["externalId"]


def test_download_media_jsoncontent_field_added_but_useless():
    """should remove jsonContent field"""
    with TemporaryDirectory() as tmp_dir:
        media_downloader = MediaDownloader(
            tmp_dir, project_id="", jsoncontent_field_added=True, project_input_type="IMAGE"
        )
        assets = [{"content": "", "externalId": "", "jsonContent": ""}]
        ret = media_downloader.download_assets(assets)[0]
        assert "jsonContent" not in ret.keys()


def test_download_media_jsoncontent_field_added_but_useful():
    """should warn jsoncontent field added and downloaded"""
    with TemporaryDirectory() as tmp_dir:
        media_downloader = MediaDownloader(
            tmp_dir, project_id="", jsoncontent_field_added=True, project_input_type="VIDEO"
        )
        assets = [
            {
                "content": "",
                "externalId": "",
                "jsonContent": "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2_video2-json-content.json",
            }
        ]
        with pytest.warns():
            media_downloader.download_assets(assets)
