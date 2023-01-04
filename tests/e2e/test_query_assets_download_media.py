"""
E2E tests for helpers.py of .assets to download media
"""

import os
import random
import time
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import requests
from PIL import Image

from kili.client import Kili
from kili.queries.asset.helpers import MediaDownloader, get_json_content_urls_video
from kili.utils.tempfile import TemporaryDirectory


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
        title="test_asset.py",
        description="test_asset.py",
    )

    with NamedTemporaryFile(mode="wb", suffix=".png") as temp:
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

        assert assets[0]["content"] == os.path.join(str(tmp_dir.resolve()), "kili_logo.png")
        assert Path(assets[0]["content"]).is_file()
        assert assets[0]["jsonContent"] == ""
        assert assets[0]["externalId"] == "kili_logo"

        assert assets[1]["content"] == os.path.join(str(tmp_dir.resolve()), "kili_logo.png")
        assert Path(assets[1]["content"]).is_file()
        assert assets[1]["jsonContent"] == ""
        assert assets[1]["externalId"] == "kili_logo.png"


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
        title="test_asset.py",
        description="test_asset.py",
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

        assert asset["content"] == ""
        frames = [filename for filename in os.listdir(tmp_dir) if filename.startswith("vid 2_")]
        assert len(frames) == 5
        assert sorted(frames)[0] == "vid 2_1"
        assert isinstance(asset["jsonContent"], list)
        assert len(asset["jsonContent"]) == 5
        assert asset["jsonContent"][0] == os.path.join(str(tmp_dir.resolve()), "vid 2_1")
        assert asset["externalId"] == "vid 2"


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
        title="test_asset.py",
        description="test_asset.py",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=["kili", "kili"],  # md5 hash: b11cc6e320a7bf4880c1d18714962f2d
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

        assert assets[0]["content"] == os.path.join(str(tmp_dir.resolve()), "text1")
        assert Path(assets[0]["content"]).is_file()
        assert assets[0]["jsonContent"] == ""
        assert assets[0]["externalId"] == "text1"

        assert assets[1]["content"] == os.path.join(str(tmp_dir.resolve()), "text1.txt")
        assert Path(assets[1]["content"]).is_file()
        assert assets[1]["jsonContent"] == ""
        assert assets[1]["externalId"] == "text1.txt"

        # asset[2] is jsoncontent richtext
        assert assets[2]["content"] == ""
        assert Path(tmp_dir / assets[2]["externalId"]).is_file()
        assert assets[2]["jsonContent"] == os.path.join(str(tmp_dir.resolve()), "richtext")
        assert assets[2]["externalId"] == "richtext"


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
        title="test_asset.py",
        description="test_asset.py",
    )

    with NamedTemporaryFile(mode="wb", suffix=".png") as temp:
        width = 4500
        height = 4500

        img = Image.new(mode="RGB", size=(width, height), color=(209, 123, 193))

        # fill image with random data to avoid image compression
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                rand_ = random.randint(0, 255)
                img.putpixel((i, j), (rand_, rand_, rand_))

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

        media_dl = MediaDownloader(
            tmp_dir,
            src_project_big_image["id"],
            jsoncontent_field_added=False,
            project_input_type="IMAGE",
        )
        asset = media_dl.download_single_asset(assets[0])

        assert Path(asset["content"]).is_file()
        assert asset["externalId"] == "randimage"
        assert isinstance(asset["jsonContent"], list)
        assert asset["jsonContent"][0]["width"] == 4500
        assert asset["jsonContent"][0]["height"] == 4500


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
        title="test_asset.py",
        description="test_asset.py",
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
        time.sleep(2)  # it takes some time for the asset to be created in the backend

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

        assert Path(asset["content"]).is_file()
        assert asset["content"] == os.path.join(str(tmp_dir.resolve()), "short_vid.mp4")
        assert asset["externalId"] == "short_vid"
        assert isinstance(asset["jsonContent"], list)
        assert len(asset["jsonContent"]) > 20
        assert Path(asset["jsonContent"][0]).is_file()
