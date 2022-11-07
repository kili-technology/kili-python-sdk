# pylint: disable=missing-docstring
import json
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import requests

from kili.orm import Asset
from kili.services.export.format.coco.common import _convert_kili_semantic_to_coco
from kili.services.types import JobName


class CocoTestCase(TestCase):
    def test__get_coco_image_annotations(self):
        with TemporaryDirectory() as tmp_dir:
            job_name = "JOB_0"
            output_file = Path(tmp_dir) / job_name / "labels.json"
            image_url = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
            r = requests.get(image_url, allow_redirects=True)
            local_file_path = Path("car_1.jpg")
            local_file_path.open("wb").write(r.content)
            _convert_kili_semantic_to_coco(
                job_name=JobName(job_name),
                assets=[
                    Asset(
                        {
                            "latestLabel": {
                                "jsonResponse": {
                                    "JOB_0": {
                                        "annotations": [
                                            {
                                                "categories": [
                                                    {"confidence": 100, "name": "OBJECT_A"}
                                                ],
                                                "jobName": "JOB_0",
                                                "mid": "2022040515434712-7532",
                                                "mlTask": "OBJECT_DETECTION",
                                                "boundingPoly": [
                                                    {
                                                        "normalizedVertices": [
                                                            {
                                                                "x": 0.0,
                                                                "y": 0.0,
                                                            },
                                                            {
                                                                "x": 1.0,
                                                                "y": 0.0,
                                                            },
                                                            {
                                                                "x": 0.0,
                                                                "y": 1.0,
                                                            },
                                                        ]
                                                    }
                                                ],
                                                "type": "semantic",
                                                "children": {},
                                            }
                                        ]
                                    },
                                    "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
                                },
                            },
                            "externalId": "car_1",
                            "jsonContent": "",
                            "content": str(local_file_path),
                        }
                    ),
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
            )
            with output_file.open("r", encoding="utf-8") as f:
                coco_annotation = json.loads(f.read())
                result = {
                    "info": {
                        "year": "2022",
                        "version": "1.0",
                        "description": "Test project - Exported from Kili Python Client",
                        "contributor": "Kili Technology",
                        "url": "https://kili-technology.com",
                    },
                    "licenses": [],
                    "categories": [
                        {"id": 1, "name": "OBJECT_B", "supercategory": ""},
                        {"id": 0, "name": "OBJECT_A", "supercategory": ""},
                    ],
                    "images": [
                        {
                            "id": 0,
                            "license": 0,
                            "file_name": "/var/folders/4d/cyyb2jg15k74pw6y661rlnm00000gn/T/tmp7ck1ykp4/data/car_1.jpg",
                            "height": 1080,
                            "width": 1920,
                            "date_captured": None,
                        }
                    ],
                    "annotations": [
                        {
                            "id": 0,
                            "image_id": 0,
                            "category_id": 0,
                            "bbox": [0, 0, 1920, 1080],
                            "segmentation": [[0.0, 0.0, 1920.0, 0.0, 0.0, 1080.0]],
                            "area": 2073600,
                            "iscrowd": 0,
                        }
                    ],
                }
                assert "Test project" in coco_annotation["info"]["description"]
                categories_by_id = {cat["id"]: cat["name"] for cat in coco_annotation["categories"]}
                assert coco_annotation["images"][0]["file_name"] == "data/car_1.jpg"
                assert coco_annotation["images"][0]["width"] == 1920
                assert coco_annotation["images"][0]["height"] == 1080
                assert coco_annotation["annotations"][0]["image_id"] == 0
                assert (
                    categories_by_id[coco_annotation["annotations"][0]["category_id"]] == "OBJECT_A"
                )
                assert coco_annotation["annotations"][0]["bbox"] == [0, 0, 1920, 1080]
                assert coco_annotation["annotations"][0]["segmentation"] == [
                    [0.0, 0.0, 1920.0, 0.0, 0.0, 1080.0]
                ]
                assert coco_annotation["annotations"][0]["area"] == 2073600

                good_date = True
                try:
                    datetime.strptime(
                        coco_annotation["info"]["date_created"], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                except ValueError:
                    good_date = False
                assert good_date, (
                    "The date is not in the right format: "
                    + coco_annotation["info"]["date_created"]
                )
