# pylint: disable=missing-module-docstring
import glob
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetExternalId, AssetFilters
from kili.domain.project import ProjectId
from kili.presentation.client.label import LabelClientMethods
from kili.services.export import AbstractExporter, export_labels
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.kili import KiliExporter
from kili.services.export.format.voc import VocExporter
from tests.fakes.fake_kili import (
    FakeKili,
    mocked_AssetQuery,
    mocked_AssetQuery_count,
    mocked_kili_api_gateway_get_project,
    mocked_ProjectQuery,
)
from tests.unit.services.export.fakes.fake_ffmpeg import mock_ffmpeg


def get_file_tree(folder: str):
    """Returns the file tree in the shape of a dictionary.

    Example:
    {
        "images": {"remote_assets.csv": {}},
        "JOB_0": {
            "labels": {
                "car_1.txt": {},
            },
            "data.yaml": {},
        },
        "JOB_1": {"labels": {}, "data.yaml": {}},
        "JOB_2": {"labels": {}, "data.yaml": {}},
        "JOB_3": {"labels": {}, "data.yaml": {}},
        "README.kili.txt": {},
    }
    """
    dct = {}
    filepaths = [
        f.replace(os.path.join(folder, ""), "")
        for f in glob.iglob(folder + "**/**", recursive=True)
    ]
    for f_p in filepaths:
        p = dct
        for x in f_p.split(os.sep):
            if len(x):
                p = p.setdefault(x, {})
    return dct


@pytest.mark.parametrize(
    ("name", "test_case"),
    [
        (
            "YOLO v5 format with split files",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "split",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "JOB_0": {
                        "labels": {
                            "car_1.txt": {},
                        },
                        "data.yaml": {},
                    },
                    "JOB_1": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "JOB_2": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "JOB_3": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v5 format with split files and download assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "split",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "images": {"car_1.jpg": {}},
                    "JOB_0": {
                        "labels": {
                            "car_1.txt": {},
                        },
                        "data.yaml": {},
                    },
                    "JOB_1": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "JOB_2": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "JOB_3": {"labels": {"car_1.txt": {}}, "data.yaml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v5 format with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "data.yaml": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v5 format with merged file and no annotation",
            {
                "export_kwargs": {
                    "project_id": "object_detection_with_empty_annotation",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "data.yaml": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v5 format with merged file and download media",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "images": {"car_1.jpg": {}},
                    "labels": {"car_1.txt": {}},
                    "data.yaml": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v4 format with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "classes.txt": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v4 format with merged file and download assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "images": {"car_1.jpg": {}},
                    "labels": {"car_1.txt": {}},
                    "classes.txt": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Kili raw format",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "raw",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"car_1.json": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Kili raw format",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "raw",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "assets": {"car_1.jpg": {}},
                    "labels": {"car_1.json": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Export to Kili raw format single file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "kili",
                    "split_option": "merged",
                    "single_file": True,
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "data.json": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "COCO format with split files",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "coco",
                    "split_option": "split",
                },
                "file_tree_expected": {
                    "data": {
                        "car_1.jpg": {},
                        "car_2.jpg": {},
                    },
                    "JOB_0": {
                        "labels.json": {},
                    },
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "COCO format with merged file",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "coco",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "data": {
                        "car_1.jpg": {},
                        "car_2.jpg": {},
                    },
                    "labels.json": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "COCO format with split files given 4 ODs with classification",
            {
                "export_kwargs": {
                    "project_id": "object_detection_with_classification",
                    "label_format": "coco",
                    "split_option": "split",
                },
                "file_tree_expected": {  # only the OD jobs have a folder.
                    "data": {
                        "car_1.jpg": {},
                    },
                    "JOB_0": {
                        "labels.json": {},
                    },
                    "JOB_1": {
                        "labels.json": {},
                    },
                    "JOB_2": {
                        "labels.json": {},
                    },
                    "JOB_3": {
                        "labels.json": {},
                    },
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Pascal VOC format with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"car_1.jpg": {}},
                    "labels": {"car_1.xml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Pascal VOC format with merged file and no annotation",
            {
                "export_kwargs": {
                    "project_id": "object_detection_with_empty_annotation",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"car_1.jpg": {}},
                    "labels": {"car_1.xml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Pascal VOC format video project",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "labels": {
                        **{f"video2_{str(i+1).zfill(3)}.xml": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.xml": {} for i in range(28)},
                    },
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "COCO format video project with split job",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "coco",
                    "split_option": "split",
                },
                "file_tree_expected": {
                    "data": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "JOB_0": {
                        "labels.json": {},
                    },
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "COCO format video project with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "coco",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "data": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "labels.json": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "YOLO v4 format video project no assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {
                        "video2_001.txt": {},
                        "video2_002.txt": {},
                        "short_video_01.txt": {},
                        "short_video_02.txt": {},
                    },
                    "README.kili.txt": {},
                    "classes.txt": {},
                    "video_meta.json": {},
                },
            },
        ),
        (
            "YOLO v4 format video project with assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "images": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "labels": {
                        "video2_001.txt": {},
                        "video2_002.txt": {},
                        "short_video_01.txt": {},
                        "short_video_02.txt": {},
                    },
                    "README.kili.txt": {},
                    "classes.txt": {},
                    "video_meta.json": {},
                },
            },
        ),
        (
            "YOLO v5 format video project with assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "images": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "labels": {
                        "video2_001.txt": {},
                        "video2_002.txt": {},
                        "short_video_01.txt": {},
                        "short_video_02.txt": {},
                    },
                    "README.kili.txt": {},
                    "data.yaml": {},
                    "video_meta.json": {},
                },
            },
        ),
        (
            "YOLO v5 format video project no assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {
                        "video2_001.txt": {},
                        "video2_002.txt": {},
                        "short_video_01.txt": {},
                        "short_video_02.txt": {},
                    },
                    "README.kili.txt": {},
                    "data.yaml": {},
                    "video_meta.json": {},
                },
            },
        ),
        (
            "Kili raw format video project with assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "raw",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "assets": {
                        **{f"video2_{str(i+1).zfill(3)}.jpg": {} for i in range(130)},
                        **{f"short_video_{str(i+1).zfill(2)}.jpg": {} for i in range(28)},
                        "short_video.mp4": {},
                    },
                    "labels": {"video2.json": {}, "short_video.json": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Kili raw format video project no assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection_video_project",
                    "label_format": "raw",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"video2.json": {}, "short_video.json": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "geojson format image project",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "geojson",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"car_1.geojson": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "geojson format image project with assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "geojson",
                    "with_assets": True,
                },
                "file_tree_expected": {
                    "labels": {"car_1.geojson": {}},
                    "images": {"car_1.jpg": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "geojson format object_detection_with_classification",
            {
                "export_kwargs": {
                    "project_id": "object_detection_with_classification",
                    "label_format": "geojson",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"car_1.geojson": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "geojson format semantic_segmentation",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "geojson",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"car_1.geojson": {}, "car_2.geojson": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "pascal voc format image project no assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "pascal_voc",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels": {"car_1.xml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "coco format image project no assets",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "coco",
                    "with_assets": False,
                },
                "file_tree_expected": {
                    "labels.json": {},
                    "README.kili.txt": {},
                },
            },
        ),
    ],
)
def test_export_service_layout(mocker: pytest_mock.MockerFixture, name, test_case):
    # mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked_ProjectQuery)
    mocker_ffmpeg = mocker.patch("kili_formats.media.video.ffmpeg")
    mocker.patch(
        "kili.services.export.format.geojson.is_geotiff_asset_with_lat_lon_coords",
        return_value=True,
    )
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)

    with TemporaryDirectory() as export_folder, TemporaryDirectory() as extract_folder:
        path_zipfile = Path(export_folder) / "export.zip"
        path_zipfile.parent.mkdir(parents=True, exist_ok=True)

        mock_ffmpeg(mocker_ffmpeg)

        fake_kili = FakeKili()
        fake_kili.kili_api_gateway.list_assets.side_effect = mocked_AssetQuery
        fake_kili.kili_api_gateway.count_assets.side_effect = mocked_AssetQuery_count
        fake_kili.kili_api_gateway.get_project.side_effect = mocked_kili_api_gateway_get_project
        default_kwargs = {
            "asset_ids": [],
            "split_option": "merged",
            "export_type": "latest",
            "single_file": False,
            "output_file": str(path_zipfile),
            "disable_tqdm": True,
            "log_level": "INFO",
            "with_assets": True,
            "annotation_modifier": None,
            "asset_filter_kwargs": None,
            "normalized_coordinates": None,
            "label_type_in": None,
            "include_sent_back_labels": None,
        }

        default_kwargs.update(test_case["export_kwargs"])

        export_labels(
            fake_kili,  # type: ignore
            **default_kwargs,
        )

        Path(extract_folder).mkdir(parents=True, exist_ok=True)
        with ZipFile(path_zipfile, "r") as z_f:
            z_f.extractall(extract_folder)

        file_tree_result = get_file_tree(extract_folder)

        file_tree_expected = test_case["file_tree_expected"]

        assert file_tree_result == file_tree_expected


@pytest.mark.parametrize(
    ("name", "test_case", "error"),
    [
        (
            "Export text classification to Yolo format to throw error",
            {
                "export_kwargs": {
                    "project_id": "text_classification",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                },
            },
            NotCompatibleInputType,
        ),
        (
            "Export Yolo format with single file to throw error",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "single_file": True,
                },
            },
            NotCompatibleOptions,
        ),
        (
            "Export Pascal VOC format with single file to throw error",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                    "single_file": True,
                },
            },
            NotCompatibleOptions,
        ),
        (
            "Export Pascal VOC format with split labels per job to throw error",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "pascal_voc",
                    "split_option": "split",
                },
            },
            NotCompatibleOptions,
        ),
        (
            "Export text classification to pascal format to throw error",
            {
                "export_kwargs": {
                    "project_id": "text_classification",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                },
            },
            NotCompatibleInputType,
        ),
        (
            "Export semantic segmentation to pascal format to throw error",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "pascal_voc",
                    "split_option": "merged",
                },
            },
            NoCompatibleJobError,
        ),
        (
            "When exporting, given an unexisting format, it throws an error",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "notexisting",
                    "split_option": "merged",
                },
            },
            ValueError,
        ),
    ],
)
@patch.object(KiliAPIGateway, "get_project", side_effect=mocked_ProjectQuery)
def test_export_service_errors(mocker_project, name, test_case, error):
    with TemporaryDirectory() as export_folder:
        path_zipfile = Path(export_folder) / "export.zip"
        path_zipfile.parent.mkdir(parents=True, exist_ok=True)

        fake_kili = FakeKili()
        fake_kili.kili_api_gateway.list_assets.side_effect = mocked_AssetQuery
        fake_kili.kili_api_gateway.count_assets.side_effect = mocked_AssetQuery_count
        fake_kili.kili_api_gateway.get_project.side_effect = mocked_kili_api_gateway_get_project
        default_kwargs = {
            "asset_ids": [],
            "split_option": "merged",
            "export_type": "latest",
            "single_file": False,
            "output_file": str(path_zipfile),
            "disable_tqdm": True,
            "log_level": "INFO",
            "with_assets": True,
            "annotation_modifier": None,
            "asset_filter_kwargs": None,
            "normalized_coordinates": None,
            "label_type_in": None,
            "include_sent_back_labels": None,
        }

        default_kwargs.update(test_case["export_kwargs"])
        with pytest.raises(error):
            export_labels(
                fake_kili,  # type: ignore
                **default_kwargs,
            )


def test_export_with_asset_filter_kwargs(mocker):
    get_project_return_val = {"jsonInterface": {}, "inputType": "", "title": ""}
    mocker.patch.object(KiliExporter, "process_and_save", return_value=None)
    mocker.patch.object(KiliExporter, "_has_data_connection", return_value=False)
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.export_labels(
        project_id="fake_proj_id",
        filename="fake_filename",
        fmt="kili",
        layout="merged",
        with_assets=False,
        asset_filter_kwargs={
            "consensus_mark_gte": 0.1,
            "consensus_mark_lte": 0.2,
            "external_id_strictly_in": ["truc"],
            "honeypot_mark_gte": 0.3,
            "honeypot_mark_lte": 0.4,
            "label_author_in": None,
            "label_reviewer_in": None,
            "skipped": None,
            "status_in": None,
            "label_category_search": None,
            "created_at_gte": "2022-02-03",
            "created_at_lte": "2023-02-03",
            "issue_type": "QUESTION",
            "issue_status": None,
            "inference_mark_gte": 0.7,
            "inference_mark_lte": 0.8,
        },
        label_type_in=["PREDICTION", "DEFAULT", "REVIEW"],
    )
    expected_where = AssetFilters(
        project_id=ProjectId("fake_proj_id"),
        external_id_strictly_in=[AssetExternalId("truc")],
        consensus_mark_gte=0.1,
        consensus_mark_lte=0.2,
        honeypot_mark_gte=0.3,
        honeypot_mark_lte=0.4,
        created_at_gte="2022-02-03",
        created_at_lte="2023-02-03",
        label_type_in=["PREDICTION", "DEFAULT", "REVIEW"],
        inference_mark_gte=0.7,
        inference_mark_lte=0.8,
        issue_type="QUESTION",
    )
    expected_fields = [
        "id",
        "externalId",
        "content",
        "jsonContent",
        "jsonMetadata",
        "status",
        "pageResolutions.pageNumber",
        "pageResolutions.height",
        "pageResolutions.width",
        "pageResolutions.rotation",
        "resolution.height",
        "resolution.width",
        "latestLabel.jsonResponse",
        "latestLabel.jsonResponseUrl",
        "latestLabel.author.id",
        "latestLabel.author.email",
        "latestLabel.author.firstname",
        "latestLabel.author.lastname",
        "latestLabel.createdAt",
        "latestLabel.isLatestLabelForUser",
        "latestLabel.isSentBackToQueue",
        "latestLabel.labelType",
        "latestLabel.modelName",
    ]
    expected_options = QueryOptions(disable_tqdm=None, first=None, skip=0)
    kili.kili_api_gateway.list_assets.assert_called_once_with(
        expected_where, expected_fields, expected_options
    )


def test_export_with_asset_filter_kwargs_unknown_arg(mocker, kili_api_gateway):
    get_project_return_val = {"jsonInterface": {}, "inputType": "", "title": ""}
    mocker.patch.object(KiliExporter, "_check_arguments_compatibility", return_value=None)
    mocker.patch.object(KiliExporter, "_check_project_compatibility", return_value=None)
    mocker.patch.object(KiliExporter, "_has_data_connection", return_value=False)
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili_api_gateway.get_project.return_value = get_project_return_val
    kili.kili_api_gateway = kili_api_gateway

    with pytest.raises(NameError, match="Unknown asset filter arguments"):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="kili",
            layout="merged",
            with_assets=False,
            asset_filter_kwargs={"this_arg_does_not_exists": 42},
        )


def mock_kili(mocker, with_data_connection):
    get_project_return_val = {
        "jsonInterface": {
            "jobs": {
                "JOB": {
                    "tools": ["rectangle"],
                    "mlTask": "OBJECT_DETECTION",
                    "content": {
                        "categories": {
                            "CLASS_A": {"name": "class A"},
                            "CLASS_B": {"name": "class B"},
                        }
                    },
                }
            }
        },
        "inputType": "IMAGE",
        "title": "",
        "description": "This is a mocked project",
        "id": "fake_proj_id",
    }

    mocker.patch.object(AbstractExporter, "_has_data_connection", return_value=with_data_connection)

    kili = LabelClientMethods()
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    return kili


def test_when_exporting_with_assets_given_a_project_with_data_connection_then_it_should_crash(
    mocker,
):
    kili = mock_kili(mocker, with_data_connection=True)
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    mocker.patch.object(AbstractExporter, "_has_data_connection", return_value=True)

    with pytest.raises(
        NotCompatibleOptions,
        match=(
            "Export with download of assets is not allowed on projects with data"
            " connections. Please disable the download of assets by setting"
            " `with_assets=False`."
        ),
    ):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="yolo_v5",
            layout="merged",
            with_assets=True,
        )


def test_when_exporting_geotiff_asset_with_incompatible_options_then_it_crashes(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            asset
            for asset in [
                {
                    "latestLabel": {
                        "author": {
                            "id": "user-feat1-1",
                            "email": "test+admin+1@kili-technology.com",
                            "firstname": "Feat1",
                            "lastname": "Test Admin",
                        },
                        "jsonResponse": {
                            "OBJECT_DETECTION_JOB": {
                                "annotations": [
                                    {
                                        "children": {},
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {"x": 4.1, "y": 52.2},
                                                    {"x": 4.5, "y": 52.7},
                                                    {"x": 4.5, "y": 52.3},
                                                    {"x": 4.1, "y": 52.4},
                                                ]
                                            }
                                        ],
                                        "categories": [{"name": "A"}],
                                        "mid": "20230719110559896-2495",
                                        "type": "rectangle",
                                    }
                                ]
                            }
                        },
                        "createdAt": "2023-07-19T09:06:03.028Z",
                        "isLatestLabelForUser": True,
                        "isSentBackToQueue": False,
                        "labelType": "DEFAULT",
                        "modelName": None,
                    },
                    "resolution": None,
                    "pageResolutions": None,
                    "id": "clk9i0hn000002a68a2zcd1v7",
                    "externalId": "sample.tif",
                    "content": (
                        "https://storage.googleapis.com/label-backend-staging/projects/clk9g"
                    ),
                    "jsonContent": [
                        {
                            "bounds": [
                                [4.472843633775792, 52.16687253311844],
                                [4.3235700288901775, 52.258603570959444],
                            ],
                            "epsg": "EPSG4326",
                            "imageUrl": "https://staging.cloud.kili-technology.com/api/label/v2/files?id=projects/clk9id",
                            "initEpsg": 4326,
                            "useClassicCoordinates": False,
                        }
                    ],
                    "jsonMetadata": {},
                }
            ]
        ],
    )

    kili = mock_kili(mocker, with_data_connection=False)
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with pytest.raises(
        NotCompatibleOptions,
        match=(
            "Cannot export geotiff assets with geospatial coordinates in coco format. Please use"
            " 'kili', 'raw' or 'geojson' formats instead."
        ),
    ):
        kili.export_labels(
            "fake_proj_id",
            "export.zip",
            fmt="coco",
        )

    with pytest.raises(
        NotCompatibleOptions,
        match=(
            "Cannot export geotiff assets with geospatial latitude and longitude coordinates with"
            " normalized_coordinates=False. Please use `normalized_coordinates=None` instead."
        ),
    ):
        kili.export_labels("fake_proj_id", "export.zip", fmt="kili", normalized_coordinates=False)


def test_given_kili_when_exporting_it_does_not_call_dataconnection_resolver(
    mocker: pytest_mock.MockerFixture,
):
    """Test that the dataconnection resolver is not called when exporting.

    Export for projects with data connections is forbidden.
    But dataConnections() resolver requires high permissions.
    This test ensures that the resolver is not called when exporting.
    """
    # Given
    project_return_val = {
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {
                            "GDGF": {
                                "children": [],
                                "color": "#472CED",
                                "name": "gdgf",
                            }
                        },
                        "input": "radio",
                    },
                    "instruction": "df",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                }
            }
        },
        "inputType": "IMAGE",
        "title": "",
        "dataConnections": None,
    }
    mocker.patch("kili.services.export.format.base.fetch_assets", return_value=[])
    process_and_save_mock = mocker.patch.object(VocExporter, "process_and_save", return_value=None)
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = project_return_val

    # When
    kili.export_labels(
        project_id="fake_proj_id", filename="exp.zip", fmt="pascal_voc", layout="merged"
    )

    # Then
    process_and_save_mock.assert_called_once()
    kili.graphql_client.execute.assert_not_called()  # pyright: ignore[reportGeneralTypeIssues]


def test_when_exporting_asset_with_include_sent_back_labels_parameter_it_filter_asset_exported(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            {
                "latestLabel": {
                    "author": {
                        "id": "user-feat1-1",
                        "email": "test+admin+1@kili-technology.com",
                        "firstname": "Feat1",
                        "lastname": "Test Admin",
                    },
                    "jsonResponse": {
                        "OBJECT_DETECTION_JOB": {
                            "annotations": [
                                {
                                    "children": {},
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 4.1, "y": 52.2},
                                                {"x": 4.5, "y": 52.7},
                                                {"x": 4.5, "y": 52.3},
                                                {"x": 4.1, "y": 52.4},
                                            ]
                                        }
                                    ],
                                    "categories": [{"name": "A"}],
                                    "mid": "20230719110559896-2495",
                                    "type": "rectangle",
                                }
                            ]
                        }
                    },
                    "createdAt": "2023-07-19T09:06:03.028Z",
                    "isLatestLabelForUser": True,
                    "isSentBackToQueue": True,
                    "labelType": "DEFAULT",
                    "modelName": None,
                },
                "resolution": None,
                "pageResolutions": None,
                "id": "clk9i0hn000002a68a2zcd1v7",
                "externalId": "BoundingBox.png",
                "content": (
                    "https://storage.googleapis.com/label-public-staging/demo-projects/Computer_vision_tutorial/BoundingBox.png"
                ),
                "jsonContent": None,
                "jsonMetadata": {},
            }
        ],
    )

    process_and_save_mock = mocker.patch.object(KiliExporter, "process_and_save", return_value=None)
    kili = mock_kili(mocker, with_data_connection=False)
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    # When
    kili.export_labels(project_id="fake_proj_id", filename="exp.zip", fmt="kili")

    # Then
    process_and_save_mock.assert_called_once()
