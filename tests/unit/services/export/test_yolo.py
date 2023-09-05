# pylint: disable=missing-docstring

from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile

import pytest_mock
import requests

from kili.adapters.http_client import HttpClient
from kili.entrypoints.queries.label import QueriesLabel
from kili.orm import Asset
from kili.services.export.format.yolo import (
    _convert_from_kili_to_yolo_format,
    _process_asset,
    _write_class_file,
)
from kili.utils.tempfile import TemporaryDirectory
from tests.fakes.fake_data import (
    asset_image_1,
    asset_image_1_without_annotation,
    asset_video,
    category_ids,
)
from tests.unit.services.export.fakes.fake_content_repository import (
    FakeContentRepository,
)


class YoloTestCase(TestCase):
    def test_process_asset_for_job_image_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository(
                    "https://contentrep",
                    HttpClient(
                        kili_endpoint="https://fake_endpoint.kili-technology.com",
                        api_key="",
                        verify=True,
                    ),
                )
                asset_remote_content, video_filenames = _process_asset(
                    asset_image_1,
                    images_folder,
                    labels_folder,
                    category_ids,
                    fake_content_repository,
                    with_assets=False,
                    project_input_type="IMAGE",
                )

                nb_files = len(
                    [name for name in labels_folder.iterdir() if (labels_folder / name).is_file()]
                )

                assert (labels_folder / "car_1.txt").is_file()
                assert nb_files == 1
                assert asset_remote_content == [
                    [
                        "car_1",
                        "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                        "car_1.txt",
                    ]
                ]
                assert len(video_filenames) == 0

    def test_process_asset_for_job_frame_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository(
                    "https://contentrep",
                    HttpClient(
                        kili_endpoint="https://fake_endpoint.kili-technology.com",
                        api_key="",
                        verify=True,
                    ),
                )
                asset_remote_content, video_filenames = _process_asset(
                    asset_video,
                    images_folder,
                    labels_folder,
                    category_ids,
                    fake_content_repository,
                    with_assets=False,
                    project_input_type="VIDEO",
                )

                nb_files = len(
                    [name for name in labels_folder.iterdir() if (labels_folder / name).is_file()]
                )

                assert nb_files == 4

                for i in range(nb_files):
                    assert (labels_folder / f"video_1_{i+1}.txt").is_file()

                expected_content = [
                    [
                        "video_1",
                        "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
                        f"video_1_{i+1}.txt",
                    ]
                    for i in range(4)
                ]
                assert asset_remote_content == expected_content

                expected_video_filenames = [f"video_1_{i+1}" for i in range(4)]
                assert len(video_filenames) == 4
                assert video_filenames == expected_video_filenames

    def test_convert_from_kili_to_yolo_format(self):
        converted_annotations = _convert_from_kili_to_yolo_format(
            "JOB_0", asset_image_1["latestLabel"], category_ids
        )
        expected_annotations = [
            (0, 0.501415026274802, 0.5296278884310182, 0.6727472455849373, 0.5381320101586394)
        ]
        assert len(converted_annotations) == 1
        assert converted_annotations == expected_annotations

    def test_convert_from_kili_to_yolo_format_no_annotation(self):
        converted_annotations = _convert_from_kili_to_yolo_format(
            "JOB_0", asset_image_1_without_annotation["latestLabel"], category_ids
        )
        assert len(converted_annotations) == 0

    def test_write_class_file_yolo_v4(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v4", "split")
            assert (directory / "classes.txt").is_file()
            with (directory / "classes.txt").open("r") as created_file:
                with open("./tests/unit/services/export/expected/classes.txt") as expected_file:
                    assert expected_file.read() == created_file.read()

    def test_write_class_file_yolo_v5(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v5", "split")
            assert (directory / "data.yaml").is_file()
            with (directory / "data.yaml").open("r") as created_file:
                with open("./tests/unit/services/export/expected/data_v5.yaml") as expected_file:
                    assert expected_file.read() == created_file.read()

    def test_write_class_file_yolo_v7(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v7", "split")
            assert (directory / "data.yaml").is_file()
            with (directory / "data.yaml").open("r") as created_file:
                with open("./tests/unit/services/export/expected/data_v7.yaml") as expected_file:
                    assert expected_file.read() == created_file.read()


get_project_return_val = {
    "jsonInterface": {
        "jobs": {
            "OBJECT_DETECTION_JOB": {
                "content": {
                    "categories": {
                        "A": {"children": [], "color": "#472CED", "name": "A"},
                        "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                    },
                    "input": "radio",
                },
                "instruction": "bbox",
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["rectangle"],
                "isChild": False,
            },
            "POLYGON_JOB": {
                "content": {
                    "categories": {
                        "F": {"children": [], "color": "#3BCADB", "name": "F"},
                        "G": {"children": [], "name": "G", "color": "#199CFC"},
                    },
                    "input": "radio",
                },
                "instruction": "polygon",
                "mlTask": "OBJECT_DETECTION",
                "required": 0,
                "tools": ["polygon"],
                "isChild": False,
            },
        }
    },
    "inputType": "IMAGE",
    "title": "fake title",
    "description": "fake desc",
    "id": "fake_proj_id",
}

assets = [
    {
        "pageResolutions": None,
        "latestLabel": {
            "author": {
                "id": "user-feat1-1",
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "lastname": "Test Admin",
                "name": "Feat1 Test Admin",
            },
            "jsonResponse": {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "children": {},
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {
                                            "x": 0.4,
                                            "y": 0.15,
                                        },
                                        {
                                            "x": 0.4,
                                            "y": 0.05,
                                        },
                                        {
                                            "x": 0.90,
                                            "y": 0.05,
                                        },
                                        {
                                            "x": 0.90,
                                            "y": 0.15,
                                        },
                                    ]
                                }
                            ],
                            "categories": [{"name": "A"}],
                            "mid": "20230802144746381-79813",
                            "type": "rectangle",
                        }
                    ]
                },
                "POLYGON_JOB": {
                    "annotations": [
                        {
                            "children": {},
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {
                                            "x": 0.75,
                                            "y": 0.23,
                                        },
                                        {
                                            "x": 0.35,
                                            "y": 0.22,
                                        },
                                        {
                                            "x": 0.07,
                                            "y": 0.35,
                                        },
                                    ]
                                }
                            ],
                            "categories": [{"name": "F"}],
                            "mid": "20230802144752750-12883",
                            "type": "polygon",
                        }
                    ]
                },
            },
            "createdAt": "2023-08-02T12:47:55.080Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "resolution": {"height": 523, "width": 474},
        "id": "clktm4x5o00002a69gv04ukst",
        "externalId": "trees",
        "content": "https://sdf",
        "jsonContent": "",
        "jsonMetadata": {},
    }
]


def test_yolo_v8_merged(mocker: pytest_mock.MockerFixture):
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch("kili.entrypoints.queries.label.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[Asset(asset) for asset in assets],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}

    kili.export_labels(
        "clktm4vzz001a0j324elr5dsy",
        filename="export_yolo_v8.zip",
        fmt="yolo_v8",
        layout="merged",
        with_assets=False,
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_yolo_v8.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()

        assert Path(f"{extract_folder}/data.yaml").read_text() == """nc: 4
names: ['OBJECT_DETECTION_JOB/A', 'OBJECT_DETECTION_JOB/B', 'POLYGON_JOB/F', 'POLYGON_JOB/G']
"""

        assert Path(f"{extract_folder}/labels").is_dir()

        label = Path(f"{extract_folder}/labels/trees.txt").read_text()

        # bbox annotation: class bbox_center_x bbox_center_y bbox_w bbox_h
        assert "0 0.65 0.1 0.5 0.09999999999999999" in label
        # polygon annotation: class x1 y1 x2 y2 x3 y3 etc
        assert "2 0.75 0.23 0.35 0.22 0.07 0.35" in label


def test_yolo_v8_split_jobs(mocker: pytest_mock.MockerFixture):
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch("kili.entrypoints.queries.label.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[Asset(asset) for asset in assets],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = {"inputType": "IMAGE"}

    kili.export_labels(
        "clktm4vzz001a0j324elr5dsy",
        filename="export_yolo_v8.zip",
        fmt="yolo_v8",
        layout="split",
        with_assets=False,
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_yolo_v8.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()
        assert Path(f"{extract_folder}/OBJECT_DETECTION_JOB/data.yaml").read_text() == """nc: 2
names: ['A', 'B']
"""
        assert Path(f"{extract_folder}/POLYGON_JOB/data.yaml").read_text() == """nc: 2
names: ['F', 'G']
"""

        assert (
            Path(f"{extract_folder}/OBJECT_DETECTION_JOB/labels/trees.txt").read_text()
            == "0 0.65 0.1 0.5 0.09999999999999999\n"
        )
        assert (
            Path(f"{extract_folder}/POLYGON_JOB/labels/trees.txt").read_text()
            == "0 0.75 0.23 0.35 0.22 0.07 0.35\n"
        )
