"""
E2E tests for helpers.py of .assets to download media
"""

import os
import random
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Union

import pytest
import requests
from PIL import Image

from kili.client import Kili
from kili.queries.asset.helpers import MediaDownloader, get_json_content_urls_video
from kili.utils.tempfile import TemporaryDirectory


def assert_helper_for_asset(
    asset: Dict,
    expected_externalid: Optional[str] = None,
    check_is_file: Optional[Union[Path, str]] = None,
    expected_content: Optional[str] = None,
    expected_json_content: Optional[Union[str, List]] = None,
):
    if expected_content is not None:
        assert asset["content"] == expected_content
    if expected_externalid is not None:
        assert asset["externalId"] == expected_externalid
    if check_is_file is not None:
        assert Path(check_is_file).is_file()
    if expected_json_content is not None:
        assert asset["jsonContent"] == expected_json_content


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def src_project_image(kili):
    """create image project with token protected url."""
    interface = {
        "jobs": {
            "DETECTION": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "instruction": "Is there a defect ? Where ? What kind ?",
                "required": 0,
                "isChild": False,
                "content": {
                    "categories": {
                        "DEFECT_CLASS_1": {"name": "defect of class 1"},
                        "DEFECT_CLASS_2": {"name": "defect of class 2"},
                        "DEFECT_CLASS_3": {"name": "defect of class 3"},
                        "DEFECT_CLASS_4": {"name": "defect of class 4"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_query_assets_download_media.py",
        description="test_query_assets_download_media.py",
    )

    with NamedTemporaryFile(mode="w+b", suffix=".png") as temp:
        with requests.get(
            "https://raw.githubusercontent.com/kili-technology/kili-python-sdk/master/docs/assets/kili_logo.png",
            timeout=20,
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                temp.write(chunk)
        kili.append_many_to_dataset(
            project_id=project["id"],
            content_array=[temp.name, temp.name],
            external_id_array=["kili_logo", "kili_logo.png"],
        )

    yield project

    kili.delete_project(project["id"])


def test_download_assets_protected_content_images(kili, src_project_image):
    """Tests with token protected content url"""
    with TemporaryDirectory() as tmp_dir:
        assets = kili.assets(
            project_id=src_project_image["id"],
            fields=["externalId", "content", "jsonContent", "project.inputType"],
        )
        media_dl = MediaDownloader(
            tmp_dir,
            src_project_image["id"],
            jsoncontent_field_added=False,
            project_input_type="IMAGE",
        )
        assets = media_dl.download_assets(assets)

        assert_helper_for_asset(
            assets[0],
            expected_externalid="kili_logo",
            check_is_file=assets[0]["content"],
            expected_content=os.path.join(str(tmp_dir.resolve()), "kili_logo.png"),
            expected_json_content="",
        )

        assert_helper_for_asset(
            assets[1],
            expected_externalid="kili_logo.png",
            check_is_file=assets[1]["content"],
            expected_content=os.path.join(str(tmp_dir.resolve()), "kili_logo.png"),
            expected_json_content="",
        )


@pytest.fixture()
def src_project_video_frames(kili):
    """create video project with token protected urls and frames"""
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A"},
                        "OBJECT_B": {"children": [], "name": "Object B"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }

    project = kili.create_project(
        input_type="VIDEO",
        json_interface=interface,
        title="test_query_assets_download_media.py",
        description="test_query_assets_download_media.py",
    )

    with TemporaryDirectory() as tmp_dir:
        urls = get_json_content_urls_video(
            "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2_video2-json-content.json"
        )
        for i, url in enumerate(urls):
            if i >= 5:  # keep only a few images for testing
                break
            with requests.get(url, stream=True, timeout=20) as response:
                response.raise_for_status()
                with open(os.path.join(tmp_dir, f"video2-img{i:06}.jpg"), "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        file.write(chunk)

        json_content_array = [
            [os.path.join(tmp_dir, filename) for filename in sorted(os.listdir(tmp_dir))]
        ]
        kili.append_many_to_dataset(
            project_id=project["id"],
            content_array=None,
            external_id_array=["vid 2"],
            json_content_array=json_content_array,
        )

    yield project

    kili.delete_project(project["id"])


def test_download_single_asset_protected_content_videos(kili, src_project_video_frames):
    """Tests with token protected content url"""
    with TemporaryDirectory() as tmp_dir:
        assets = kili.assets(
            project_id=src_project_video_frames["id"],
            fields=["externalId", "content", "jsonContent", "project.inputType"],
        )

        media_dl = MediaDownloader(
            tmp_dir,
            src_project_video_frames["id"],
            jsoncontent_field_added=False,
            project_input_type="VIDEO",
        )
        asset = media_dl.download_single_asset(assets[0])

        assert_helper_for_asset(
            asset,
            expected_content="",
            expected_externalid="vid 2",
            check_is_file=asset["jsonContent"][0],
            expected_json_content=[
                os.path.join(str(tmp_dir.resolve()), f"vid 2_{i+1}") for i in range(5)
            ],
        )


@pytest.fixture()
def src_project_text(kili):
    """create text project with normal text and richtext"""
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "CLASS_A": {"children": [], "name": "Class A"},
                        "CLASS_B": {"children": [], "name": "Class B"},
                    },
                    "input": "radio",
                },
                "instruction": "Choose between class A and class B:",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }

    project = kili.create_project(
        input_type="TEXT",
        json_interface=interface,
        title="test_query_assets_download_media.py",
        description="test_query_assets_download_media.py",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=["kili", "kili"],
        external_id_array=["text1", "text1.txt"],
        json_content_array=None,
    )

    json_content_array = [
        [
            {
                "children": [
                    {
                        "id": "42",
                        "bold": True,
                        "underline": True,
                        "text": (
                            "The unanimous Declaration of the thirteen United States of America."
                        ),
                    }
                ]
            }
        ]
    ]
    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=None,
        external_id_array=["richtext"],
        json_content_array=json_content_array,
    )

    yield project

    kili.delete_project(project["id"])


def test_download_assets_text(kili, src_project_text):
    """test download_assets on text project"""
    with TemporaryDirectory() as tmp_dir:
        assets = kili.assets(
            project_id=src_project_text["id"],
            fields=["externalId", "content", "jsonContent", "project.inputType"],
        )

        media_dl = MediaDownloader(
            tmp_dir,
            src_project_text["id"],
            jsoncontent_field_added=False,
            project_input_type="TEXT",
        )
        assets = media_dl.download_assets(assets)

        assert_helper_for_asset(
            assets[0],
            expected_externalid="text1",
            check_is_file=assets[0]["content"],
            expected_content=os.path.join(str(tmp_dir.resolve()), "text1"),
            expected_json_content="",
        )
        assert_helper_for_asset(
            assets[1],
            expected_externalid="text1.txt",
            check_is_file=assets[1]["content"],
            expected_content=os.path.join(str(tmp_dir.resolve()), "text1.txt"),
            expected_json_content="",
        )
        # asset[2] is jsoncontent richtext
        assert_helper_for_asset(
            assets[2],
            expected_externalid="richtext",
            check_is_file=assets[2]["jsonContent"],
            expected_content="",
            expected_json_content=os.path.join(str(tmp_dir.resolve()), "richtext"),
        )


@pytest.fixture()
def src_project_big_image(kili):
    """create image project with big images and jsonContent"""
    interface = {
        "jobs": {
            "DETECTION": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "instruction": "Is there a defect ? Where ? What kind ?",
                "required": 0,
                "isChild": False,
                "content": {
                    "categories": {
                        "DEFECT_CLASS_1": {"name": "defect of class 1"},
                        "DEFECT_CLASS_2": {"name": "defect of class 2"},
                        "DEFECT_CLASS_3": {"name": "defect of class 3"},
                        "DEFECT_CLASS_4": {"name": "defect of class 4"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_query_assets_download_media.py",
        description="test_query_assets_download_media.py",
    )

    with NamedTemporaryFile(mode="w+b", suffix=".png") as temp:
        width = 3800
        height = 3800

        img = Image.new(mode="RGB", size=(width, height))

        # fill image with random data to avoid image compression
        random_data = [random.randint(0, 255) for _ in range(width * height)]
        img.putdata(list(zip(random_data, random_data, random_data)))  # type: ignore

        img.save(temp, "PNG")
        kili.append_many_to_dataset(
            project_id=project["id"],
            content_array=[temp.name],
            external_id_array=["randimage"],
        )

    count_assets = 0
    while count_assets < 1:
        count_assets = kili.count_assets(
            project_id=project["id"],
        )
        time.sleep(2)  # it takes some time for the asset to be created in the backend

    yield project

    kili.delete_project(project["id"])


def test_download_single_asset_big_image(kili, src_project_big_image):
    """test upload big image"""
    with TemporaryDirectory() as tmp_dir:
        assets = kili.assets(
            project_id=src_project_big_image["id"],
            fields=["externalId", "content", "jsonContent", "project.inputType"],
        )

        assert assets[0]["jsonContent"] != ""

        media_dl = MediaDownloader(
            tmp_dir,
            src_project_big_image["id"],
            jsoncontent_field_added=False,
            project_input_type="IMAGE",
        )
        asset = media_dl.download_single_asset(assets[0])

        assert_helper_for_asset(
            asset,
            expected_externalid="randimage",
            check_is_file=asset["content"],
            expected_content=os.path.join(str(tmp_dir.resolve()), "randimage.png"),
        )


@pytest.fixture()
def src_project_video_content_and_jsoncontent(kili):
    """create video project with both content and json content"""
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A"},
                        "OBJECT_B": {"children": [], "name": "Object B"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }

    project = kili.create_project(
        input_type="VIDEO",
        json_interface=interface,
        title="test_query_assets_download_media.py",
        description="test_query_assets_download_media.py",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        ],
        external_id_array=["short_vid"],
        json_content_array=None,
        json_metadata_array=[
            {
                "processingParameters": {
                    "shouldKeepNativeFrameRate": True,
                    "shouldUseNativeVideo": False,
                }
            },
        ],
    )

    count_assets = 0
    while count_assets < 1:
        count_assets = kili.count_assets(
            project_id=project["id"],
        )
        time.sleep(2)  # it takes some time for the frames to be created in the backend

    yield project

    kili.delete_project(project["id"])


def test_download_single_asset_video_content_and_jsoncontent(
    kili, src_project_video_content_and_jsoncontent
):
    """test video content and jsoncontent"""
    with TemporaryDirectory() as tmp_dir:
        assets = kili.assets(
            project_id=src_project_video_content_and_jsoncontent["id"],
            fields=["externalId", "content", "jsonContent", "project.inputType"],
        )

        media_dl = MediaDownloader(
            tmp_dir,
            src_project_video_content_and_jsoncontent["id"],
            jsoncontent_field_added=False,
            project_input_type="VIDEO",
        )
        asset = media_dl.download_single_asset(assets[0])

        assert_helper_for_asset(
            asset,
            expected_externalid="short_vid",
            check_is_file=asset["jsonContent"][0],
            expected_json_content=[
                os.path.join(str(tmp_dir.resolve()), f"short_vid_{f'{i+1}'.zfill(2)}")
                for i in range(28)  # 28 frames in video short_video.mp4
            ],
        )
