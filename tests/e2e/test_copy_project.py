"""Tests for copy project service."""

import hashlib
from pathlib import Path
from typing import Union

import pytest

from kili.client import Kili
from kili.services.copy_project import ProjectCopier
from kili.utils.tempfile import TemporaryDirectory

json_response_a = {
    "0": {},
    "1": {},
    "2": {},
    "3": {},
    "4": {},
    "5": {},
    "6": {},
    "7": {},
    "8": {},
    "9": {},
    "10": {},
    "11": {},
    "12": {},
    "13": {},
    "14": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": True}},
    "15": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "16": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "17": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "18": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "19": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "20": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "21": {"JOB_0": {"categories": [{"name": "OBJECT_A"}], "isKeyFrame": False}},
    "22": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": True}},
    "23": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "24": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "25": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "26": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "27": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "28": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "29": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
}

json_response_b = {
    "0": {},
    "1": {},
    "2": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": True}},
    "3": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
    "4": {"JOB_0": {"categories": [{"name": "OBJECT_B"}], "isKeyFrame": False}},
}


@pytest.fixture()
def src_project_video(kili: "Kili"):
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
        title="test_e2e_copy_project_video.py",
    )

    kili.update_properties_in_project(
        project_id=project["id"],
        consensus_tot_coverage=0,
        min_consensus_size=1,
        review_coverage=0,
    )

    kili.append_to_roles(
        project_id=project["id"], user_email="test1@kili-technology.com", role="LABELER"
    )
    kili.append_to_roles(
        project_id=project["id"], user_email="test2@kili-technology.com", role="LABELER"
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4",
        ],
        external_id_array=["short_vid"],
    )
    kili.append_many_to_dataset(
        project["id"],
        content_array=None,
        external_id_array=["jsoncontent_vid"],
        json_content_array=[
            [
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000001.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000002.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000003.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000004.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000005.jpg",
            ]
        ],
    )
    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"
        ],
        external_id_array=["short_vid_split"],
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

    assets = kili.assets(project_id=project["id"], fields=["externalId", "id"])
    asset_id_array = [x["id"] for x in assets]
    members = kili.project_users(
        project_id=project["id"], fields=["user.id", "activated", "user.email", "status"]
    )
    members_id_array = [
        x["user"]["id"] for x in members if x["status"] != "ORG_SUSPENDED" and x["activated"]
    ]
    assert kili.count_labels(project_id=project["id"]) == 0, f"{kili.labels(project['id'])}"
    kili.append_labels(
        [asset_id_array[0]],
        json_response_array=[json_response_a],
        author_id_array=[members_id_array[0]],
        seconds_to_label_array=[1],
        model_name=None,
        label_type="DEFAULT",
    )
    assert kili.count_labels(project_id=project["id"]) == 1, f"{kili.labels(project['id'])}"
    kili.create_predictions(
        project_id=project["id"],
        asset_id_array=[asset_id_array[1]],
        json_response_array=[json_response_b],
        model_name="yolo",
    )
    assert kili.count_labels(project_id=project["id"]) == 2, f"{kili.labels(project['id'])}"
    kili.create_predictions(
        project_id=project["id"],
        asset_id_array=[asset_id_array[1]],
        json_response_array=[json_response_b],
        model_name="unet",
    )
    assert kili.count_labels(project_id=project["id"]) == 3, f"{kili.labels(project['id'])}"
    kili.append_labels(
        [asset_id_array[2]],
        json_response_array=[{}],
        author_id_array=None,
        seconds_to_label_array=[24],
        model_name=None,
        label_type="REVIEW",
    )
    assert kili.count_labels(project_id=project["id"]) == 4, f"{kili.labels(project['id'])}"

    yield project

    kili.delete_project(project["id"])


def md5_hash(filepath: Union[str, Path]):
    """Get md5 hash of file at filepath."""
    return hashlib.md5(open(filepath, "rb").read()).hexdigest()


def test_copy_project_e2e_video(kili: "Kili", src_project_video):
    new_proj_id = kili.copy_project(
        from_project_id=src_project_video["id"],
        description="new description",
        copy_assets=True,
        copy_labels=True,
    )

    proj_fields = (
        ProjectCopier.FIELDS_PROJECT
        + ProjectCopier.FIELDS_QUALITY_SETTINGS
        + ProjectCopier.FIELDS_JSON_INTERFACE
    )

    src_proj = kili.projects(project_id=src_project_video["id"], fields=proj_fields)[0]  # type: ignore
    new_proj = kili.projects(project_id=new_proj_id, fields=proj_fields)[0]  # type: ignore

    members_src = kili.project_users(
        project_id=src_proj["id"],
        fields=["activated", "role", "user.email", "status"],
    )
    members_new = kili.project_users(
        project_id=new_proj_id,
        fields=["activated", "role", "user.email", "status"],
    )

    label_fields = [
        "author.email",
        "jsonResponse",
        "secondsToLabel",
        "isLatestLabelForUser",
        "labelOf.externalId",
        "labelType",
        "modelName",
    ]
    labels_src = kili.labels(project_id=src_proj["id"], fields=label_fields)
    labels_src = [label for label in labels_src if label["isLatestLabelForUser"]]
    labels_new = kili.labels(project_id=new_proj_id, fields=label_fields)

    # assert project
    assert new_proj["title"].startswith(src_proj["title"])
    assert "copy" in new_proj["title"]
    assert new_proj["description"] == "new description"
    assert new_proj["inputType"] == src_proj["inputType"]
    assert new_proj["jsonInterface"] == src_proj["jsonInterface"]

    # assert quality settings
    for field_name in ProjectCopier.FIELDS_QUALITY_SETTINGS:
        assert new_proj[field_name] == src_proj[field_name]

    # assert members
    members_src = sorted(members_src, key=lambda member: member["user"]["email"])
    members_new = sorted(members_new, key=lambda member: member["user"]["email"])
    assert members_src == members_new

    # assert labels
    assert len(labels_src) == len(labels_new) == 4
    label_sort_key = lambda label: (
        label["secondsToLabel"],
        label["labelOf"]["externalId"],
        label["labelType"],
        label["modelName"],
    )
    labels_src = sorted(labels_src, key=label_sort_key)
    labels_new = sorted(labels_new, key=label_sort_key)
    assert labels_src == labels_new

    # assert assets
    with TemporaryDirectory() as tmp_dir:
        assets_src = kili.assets(
            project_id=src_proj["id"],
            fields=["externalId", "content"],
            disable_tqdm=True,
            download_media=True,
            local_media_dir=str(tmp_dir / "src_dir"),
        )
        assets_new = kili.assets(
            project_id=new_proj_id,
            fields=["externalId", "content"],
            disable_tqdm=True,
            download_media=True,
            local_media_dir=str(tmp_dir / "new_dir"),
        )

        assets_src = sorted(assets_src, key=lambda asset: asset["externalId"])
        assets_new = sorted(assets_new, key=lambda asset: asset["externalId"])
        for asset_src, asset_new in zip(assets_src, assets_new):
            assert asset_src["externalId"] == asset_new["externalId"]

            if Path(asset_src["content"]).is_file():
                assert md5_hash(asset_src["content"]) == md5_hash(asset_new["content"])
            else:
                assert asset_src["content"] == asset_new["content"]

            if isinstance(asset_src["jsonContent"], list):
                assert len(asset_src["jsonContent"]) == len(asset_new["jsonContent"])
            else:
                assert asset_src["jsonContent"] == asset_new["jsonContent"]

    kili.delete_project(new_proj_id)


@pytest.fixture()
def src_project_image_ocr(kili):
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": ["JOB_1"], "name": "Object A", "color": "#733AFB"}
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "tools": ["rectangle"],
                "mlTask": "OBJECT_DETECTION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
            "JOB_1": {
                "content": {"input": "radio"},
                "instruction": "Transcription of A",
                "isChild": True,
                "mlTask": "TRANSCRIPTION",
                "models": {},
                "isVisible": True,
                "required": 1,
            },
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_e2e_copy_project_image.py",
    )

    full_text_annotations = {
        "fullTextAnnotation": {"pages": [{"height": 1029, "width": 1572}]},
        "textAnnotations": [
            {
                "description": "NEDERLANDSE",
                "boundingPoly": {
                    "vertices": [
                        {"x": 74, "y": 72},
                        {"x": 462, "y": 72},
                        {"x": 462, "y": 122},
                        {"x": 74, "y": 122},
                    ]
                },
            }
        ],
    }

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/OCR/Dutch_identity_card_front_specimen_issued_9_March_2014.jpg",
        ],
        external_id_array=["id_card"],
        json_metadata_array=[full_text_annotations],
    )

    yield project

    kili.delete_project(project["id"])


def test_copy_project_e2e_with_ocr_metadata(kili: Kili, src_project_image_ocr):
    new_proj_id = kili.copy_project(
        from_project_id=src_project_image_ocr["id"],
        description="new description",
        copy_assets=True,
        copy_labels=True,
    )

    assets_src = kili.assets(
        src_project_image_ocr["id"],
        fields=["ocrMetadata", "content", "externalId"],
        download_media=True,
    )
    assets_new = kili.assets(
        new_proj_id, fields=["ocrMetadata", "content", "externalId"], download_media=True
    )

    assert assets_src[0]["ocrMetadata"] == assets_new[0]["ocrMetadata"]

    assert assets_new[0]["ocrMetadata"]["textAnnotations"][0]["description"] == "NEDERLANDSE"

    kili.delete_project(new_proj_id)
