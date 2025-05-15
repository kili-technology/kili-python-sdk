import json
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pytest_mock
from kili_formats import convert_from_kili_to_coco_format
from kili_formats.types import JobTool
from PIL import Image

from kili.presentation.client.label import LabelClientMethods
from kili.services.export.format.base import AbstractExporter
from kili.utils.tempfile import TemporaryDirectory

from .helpers import coco as helpers


def test__convert_from_kili_to_coco_format():
    with TemporaryDirectory() as tmp_dir:
        job_name = "JOB_0"
        local_file_path = tmp_dir / Path("image1.jpg")
        image_width = 1920
        image_height = 1080
        Image.new("RGB", (image_width, image_height)).save(local_file_path)
        labels_json = convert_from_kili_to_coco_format(
            jobs={
                job_name: {
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
                    "tools": [JobTool.SEMANTIC],
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
            title="Test project",
            project_input_type="IMAGE",
            annotation_modifier=lambda x, _, _1: x,
            merged=False,
        )
        if isinstance(labels_json, tuple):
            labels_json = labels_json[0]

        assert "Test project" in labels_json["info"]["description"]
        categories_by_id = {cat["id"]: cat["name"] for cat in labels_json["categories"]}
        assert labels_json["images"][0]["file_name"] == "data/image1.jpg"
        assert labels_json["images"][0]["width"] == 1920
        assert labels_json["images"][0]["height"] == 1080
        assert labels_json["annotations"][0]["image_id"] == 0
        assert categories_by_id[labels_json["annotations"][0]["category_id"]] == "OBJECT_A"
        assert labels_json["annotations"][0]["bbox"] == [0, 0, 960, 540]
        assert labels_json["annotations"][0]["segmentation"] == [[0.0, 0.0, 960.0, 0.0, 0.0, 540.0]]
        # Area of a triangle: base * height / 2
        assert labels_json["annotations"][0]["area"] == 960.0 * 540.0 / 2

        good_date = True
        try:
            datetime.strptime(labels_json["info"]["date_created"], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            good_date = False
        assert good_date, (
            "The date is not in the right format: " + labels_json["info"]["date_created"]
        )


def test__export_in_coco_format(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {
                            "OBJECT_A": {
                                "children": [],
                                "color": "#472CED",
                                "name": "object A",
                                "id": "category1",
                            }
                        },
                        "input": "radio",
                    },
                    "instruction": "",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 0,
                    "tools": ["semantic"],
                    "isChild": False,
                    "isNew": False,
                },
                "OBJECT_DETECTION_JOB_0": {
                    "content": {
                        "categories": {
                            "OBJECT_B": {
                                "children": [],
                                "color": "#5CE7B7",
                                "name": "object B",
                                "id": "category2",
                            }
                        },
                        "input": "radio",
                    },
                    "instruction": "",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 0,
                    "tools": ["semantic"],
                    "isChild": False,
                    "isNew": False,
                },
            }
        },
        "inputType": "IMAGE",
        "title": "Image project",
        "description": "",
        "id": "fake_proj_id",
        "dataConnections": None,
    }

    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=list(
            json.load(
                Path("./tests/unit/services/export/fakes/image_project_assets_for_coco.json").open()
            )
        ),
    )
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_file = Path(export_folder) / "export_coco.zip"

        kili.export_labels(
            "fake_proj_id",
            str(export_file),
            fmt="coco",
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_file, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            jobs = [
                "OBJECT_DETECTION_JOB",
                "OBJECT_DETECTION_JOB_0",
            ]
            assert Path(f"{extract_folder}/{jobs[0]}/labels.json").is_file()

            with Path(f"{extract_folder}/{jobs[0]}/labels.json").open() as f:
                output1 = json.load(f)

            assert Path(f"{extract_folder}/{jobs[1]}/labels.json").is_file()

            with Path(f"{extract_folder}/{jobs[1]}/labels.json").open() as f:
                output2 = json.load(f)

    assert "Image project" in output1["info"]["description"]
    assert len(output1["annotations"]) == 6
    assert len(output1["images"]) == 3
    assert "Image project" in output2["info"]["description"]
    assert len(output2["annotations"]) == 5
    assert len(output2["images"]) == 3
