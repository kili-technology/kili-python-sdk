# pylint: disable=missing-docstring
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
from PIL import Image

from kili.orm import Asset
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.format.coco import (
    CocoExporter,
    _convert_kili_semantic_to_coco,
    _get_coco_geometry_from_kili_bpoly,
)
from kili.services.types import Job, JobName
from kili.utils.tempfile import TemporaryDirectory

from .helpers import coco as helpers


def test__get_coco_image_annotations():
    with TemporaryDirectory() as tmp_dir:
        job_name = "JOB_0"
        output_file = Path(tmp_dir) / job_name / "labels.json"
        local_file_path = tmp_dir / Path("image1.jpg")
        image_width = 1920
        image_height = 1080
        Image.new("RGB", (image_width, image_height)).save(local_file_path)
        _convert_kili_semantic_to_coco(
            job_name=JobName(job_name),
            assets=[
                helpers.get_asset(
                    local_file_path,
                    with_annotation=[
                        {
                            "x": 0.0,
                            "y": 0.0,
                        },
                        {
                            "x": 0.5,
                            "y": 0.0,
                        },
                        {
                            "x": 0.0,
                            "y": 0.5,
                        },
                    ],
                )
            ],
            output_dir=Path(tmp_dir),
            job={
                "mlTask": "OBJECT_DETECTION",
                "content": {
                    "categories": {
                        "OBJECT_A": {"name": "Object A"},
                        "OBJECT_B": {"name": "Object B"},
                    }
                },
                "instruction": "",
                "isChild": False,
                "isNew": False,
                "isVisible": True,
                "models": {},
                "required": True,
                "tools": ["semantic"],
            },
            title="Test project",
            project_input_type="IMAGE",
            annotation_modifier=lambda x, _, _1: x,
        )
        with output_file.open("r", encoding="utf-8") as f:
            coco_annotation = json.loads(f.read())

            assert "Test project" in coco_annotation["info"]["description"]
            categories_by_id = {cat["id"]: cat["name"] for cat in coco_annotation["categories"]}
            assert coco_annotation["images"][0]["file_name"] == "data/image1.jpg"
            assert coco_annotation["images"][0]["width"] == 1920
            assert coco_annotation["images"][0]["height"] == 1080
            assert coco_annotation["annotations"][0]["image_id"] == 0
            assert categories_by_id[coco_annotation["annotations"][0]["category_id"]] == "OBJECT_A"
            assert coco_annotation["annotations"][0]["bbox"] == [0, 0, 960, 540]
            assert coco_annotation["annotations"][0]["segmentation"] == [
                [0.0, 0.0, 960.0, 0.0, 0.0, 540.0]
            ]
            assert coco_annotation["annotations"][0]["area"] == 2073600

            good_date = True
            try:
                datetime.strptime(coco_annotation["info"]["date_created"], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                good_date = False
            assert good_date, (
                "The date is not in the right format: " + coco_annotation["info"]["date_created"]
            )


@pytest.mark.parametrize(
    "name,normalized_vertices,expected_angle,expected_bounding_box",
    [
        (
            "rotated bbox",
            [
                {"x": 0.29542394060228344, "y": 0.5619730837117777},
                {"x": 0.36370176857458425, "y": 0.4036476855151382},
                {"x": 0.4595066260060737, "y": 0.5342261578662051},
                {"x": 0.3912287980337728, "y": 0.6925515560628448},
            ],
            37.47617956136133,
            [698.3073956632018, 435.93950035634924, 231.7840874775929, 215.46126441579023],
        ),
        (
            "horizontal bbox",
            [
                {"x": 0.57214895419755, "y": 0.8004988292446383},
                {"x": 0.57214895419755, "y": 0.5027584456173183},
                {"x": 0.6435613050929351, "y": 0.5027584456173183},
                {"x": 0.6435613050929351, "y": 0.8004988292446383},
            ],
            0.0,
            [1098.525992059296, 542.9791212667037, 137.1117137191393, 321.55961431750563],
        ),
    ],
)
def test__get_coco_image_annotations_with_label_modifier(
    name, normalized_vertices, expected_angle, expected_bounding_box
):
    with TemporaryDirectory() as tmp_dir:
        job_name = "JOB_0"
        output_file = Path(tmp_dir) / job_name / "labels.json"

        image_width = 1920
        image_height = 1080
        local_file_path = tmp_dir / Path("image1.jpg")
        Image.new("RGB", (image_width, image_height)).save(local_file_path)

        area = 2073600

        expected_segmentation = [
            a for p in normalized_vertices for a in [p["x"] * image_width, p["y"] * image_height]
        ]

        _convert_kili_semantic_to_coco(
            job_name=JobName(job_name),
            assets=[
                helpers.get_asset(
                    local_file_path,
                    with_annotation=normalized_vertices,
                )
            ],
            output_dir=Path(tmp_dir),
            job={
                "mlTask": "OBJECT_DETECTION",
                "content": {
                    "categories": {
                        "OBJECT_A": {"name": "Object A"},
                        "OBJECT_B": {"name": "Object B"},
                    }
                },
                "instruction": "",
                "isChild": False,
                "isNew": False,
                "isVisible": True,
                "models": {},
                "required": True,
                "tools": ["semantic"],
            },
            title="Test project",
            project_input_type="IMAGE",
            annotation_modifier=helpers.estimate_rotated_bb_from_kili_poly,
        )

        with output_file.open("r", encoding="utf-8") as f:
            coco_annotation = json.loads(f.read())

            #### DON'T DELETE - for debugging #####
            # helpers.display_kili_and_coco_bbox(
            # local_file_path, expected_segmentation, coco_annotation
            # )
            ##########

            assert "Test project" in coco_annotation["info"]["description"]
            categories_by_id = {cat["id"]: cat["name"] for cat in coco_annotation["categories"]}
            assert coco_annotation["images"][0]["file_name"] == "data/image1.jpg"
            assert coco_annotation["images"][0]["width"] == image_width
            assert coco_annotation["images"][0]["height"] == image_height
            assert coco_annotation["annotations"][0]["image_id"] == 0
            assert categories_by_id[coco_annotation["annotations"][0]["category_id"]] == "OBJECT_A"
            assert coco_annotation["annotations"][0]["bbox"] == pytest.approx(expected_bounding_box)
            assert coco_annotation["annotations"][0]["attributes"] == {"rotation": expected_angle}
            assert coco_annotation["annotations"][0]["segmentation"][0] == pytest.approx(
                expected_segmentation
            )
            assert coco_annotation["annotations"][0]["area"] == area

            good_date = True
            try:
                datetime.strptime(coco_annotation["info"]["date_created"], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                good_date = False
            assert good_date, (
                "The date is not in the right format: " + coco_annotation["info"]["date_created"]
            )


def test__get_coco_image_annotations_without_annotation():
    with TemporaryDirectory() as tmp_dir:
        job_name = "JOB_0"
        output_file = Path(tmp_dir) / job_name / "labels.json"
        local_file_path = tmp_dir / Path("image1.jpg")
        image_width = 1920
        image_height = 1080
        Image.new("RGB", (image_width, image_height)).save(local_file_path)
        _convert_kili_semantic_to_coco(
            job_name=JobName(job_name),
            assets=[
                helpers.get_asset(
                    local_file_path,
                    with_annotation=None,
                )
            ],
            output_dir=Path(tmp_dir),
            job={
                "mlTask": "OBJECT_DETECTION",
                "content": {
                    "categories": {
                        "OBJECT_A": {"name": "Object A"},
                        "OBJECT_B": {"name": "Object B"},
                    }
                },
                "instruction": "",
                "isChild": False,
                "isNew": False,
                "isVisible": True,
                "models": {},
                "required": True,
                "tools": ["semantic"],
            },
            title="Test project",
            project_input_type="IMAGE",
            annotation_modifier=lambda x, _, _1: x,
        )

        with output_file.open("r", encoding="utf-8") as f:
            coco_annotation = json.loads(f.read())

            assert "Test project" in coco_annotation["info"]["description"]
            assert coco_annotation["images"][0]["file_name"] == "data/image1.jpg"
            assert coco_annotation["images"][0]["width"] == 1920
            assert coco_annotation["images"][0]["height"] == 1080
            assert len(coco_annotation["annotations"]) == 0


@pytest.mark.parametrize(
    "jobs,expected_error",
    [
        ({"JOB_0": {"tools": ["rectangle"], "mlTask": "SPEECH_TO_TEXT"}}, NoCompatibleJobError),
        ({"JOB_0": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}, None),
        (
            {
                "JOB_0": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"},
                "OBJECT_DETECTION_JOB": {"mlTask": "OBJECT_DETECTION", "tools": ["rectangle"]},
            },
            None,
        ),
        (
            {
                "JOB_0": {"tools": ["faketool"], "mlTask": "OBJECT_DETECTION"},
                "OBJECT_DETECTION_JOB": {"mlTask": "OBJECT_DETECTION", "tools": ["rectangle"]},
            },
            None,  # OBJECT_DETECTION_JOB is valid job
        ),
        (
            {
                "JOB_0": {"tools": ["tool1"], "mlTask": "OBJECT_DETECTION"},
                "OBJECT_DETECTION_JOB": {"mlTask": "OBJECT_DETECTION", "tools": ["tool2"]},
            },
            NoCompatibleJobError,
        ),
    ],
)
@patch.object(CocoExporter, "__init__", lambda x: None)
def test__check_project_compatibility(jobs, expected_error):
    exporter = CocoExporter()
    exporter.project_input_type = "IMAGE"
    exporter.project_json_interface = {"jobs": jobs}
    if expected_error:
        with pytest.raises(expected_error):
            exporter._check_project_compatibility()


def test_coco_video_jsoncontent():
    json_interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "color": "#472CED", "name": "A"},
                        "OBJECT_B": {"children": [], "name": "B", "color": "#5CE7B7"},
                    },
                    "input": "radio",
                },
                "instruction": "dfgdfg",
                "mlTask": "OBJECT_DETECTION",
                "required": 1,
                "tools": ["rectangle"],
                "isChild": False,
                "models": {"tracking": {}},
            }
        }
    }
    job_object_detection = {
        "JOB_0": {
            "annotations": [
                {
                    "categories": [{"confidence": 100, "name": "OBJECT_A"}],
                    "jobName": "JOB_0",
                    "mid": "2022040515434712-7532",
                    "mlTask": "OBJECT_DETECTION",
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.16504140348233334, "y": 0.7986938935103378},
                                {"x": 0.16504140348233334, "y": 0.2605618833516984},
                                {"x": 0.8377886490672706, "y": 0.2605618833516984},
                                {"x": 0.8377886490672706, "y": 0.7986938935103378},
                            ]
                        }
                    ],
                    "type": "rectangle",
                    "children": {},
                }
            ]
        }
    }
    asset_video_no_content_and_json_content = {
        "latestLabel": {
            "jsonResponse": {
                "0": {},
                "1": job_object_detection,
                "2": job_object_detection,
                **{str(i): {} for i in range(3, 5)},
            },
            "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
        },
        "externalId": "video2",
        "content": "",
        "jsonContent": [],
    }
    # fill asset with jsonContent frames on disk
    with TemporaryDirectory() as tmp_dir_for_frames:
        for i, filelink in enumerate(
            [
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000001.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000002.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000003.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000004.jpg",
                "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000005.jpg",
            ]
        ):
            filepath = (
                Path(tmp_dir_for_frames)
                / f'{asset_video_no_content_and_json_content["externalId"]}_{i+1}.jpg'
            )
            with open(filepath, "wb") as f:
                f.write(requests.get(filelink, timeout=20).content)
            asset_video_no_content_and_json_content["jsonContent"].append(filepath)

        with TemporaryDirectory() as tmp_dir:
            labels_json, _ = _convert_kili_semantic_to_coco(
                job_name=JobName("JOB_0"),
                assets=[Asset(asset_video_no_content_and_json_content)],
                output_dir=Path(tmp_dir),
                job=Job(**json_interface["jobs"]["JOB_0"]),
                title="test",
                project_input_type="VIDEO",
                annotation_modifier=lambda x, _, _1: x,
            )

            assert len(labels_json["images"]) == 5
            assert len(labels_json["annotations"]) == 2  # 2 frames with annotations

            assert [img["file_name"] for img in labels_json["images"]] == [
                f"data/video2_{i+1}.jpg" for i in range(5)
            ]

            assert labels_json["annotations"][0]["image_id"] == 2
            assert labels_json["annotations"][1]["image_id"] == 3


def test_get_coco_geometry_from_kili_bpoly():
    boundingPoly = [
        {
            "normalizedVertices": [
                {"x": 0.1, "y": 0.1},
                {"x": 0.1, "y": 0.4},
                {"x": 0.8, "y": 0.4},
                {"x": 0.8, "y": 0.1},
            ]
        }
    ]
    image_width, image_height = 1920, 1080
    bbox, poly = _get_coco_geometry_from_kili_bpoly(boundingPoly, image_width, image_height)
    assert bbox == [192, 108, 1344, 324]
    assert bbox[0] == int(0.1 * image_width)
    assert bbox[1] == int(0.1 * image_height)
    assert bbox[2] == int((0.8 - 0.1) * image_width)
    assert bbox[3] == int((0.4 - 0.1) * image_height)
    assert poly == [192.0, 108.0, 192.0, 432.0, 1536.0, 432.0, 1536.0, 108.0]
