import json
from datetime import datetime
from pathlib import Path

from kili_formats import convert_from_kili_to_coco_format
from PIL import Image

from kili.services.types import JobName
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
        _, paths = convert_from_kili_to_coco_format(
            jobs={
                JobName(job_name): {
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
                }
            },
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
            title="Test project",
            project_input_type="IMAGE",
            annotation_modifier=lambda x, _, _1: x,
            merged=False,
        )

        assert paths[0] == output_file
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
            # Area of a triangle: base * height / 2
            assert coco_annotation["annotations"][0]["area"] == 960.0 * 540.0 / 2

            good_date = True
            try:
                datetime.strptime(coco_annotation["info"]["date_created"], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                good_date = False
            assert good_date, (
                "The date is not in the right format: " + coco_annotation["info"]["date_created"]
            )
