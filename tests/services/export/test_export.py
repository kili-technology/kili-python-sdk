# pylint: disable=missing-module-docstring
import glob
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import pytest
import pytest_mock

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.entrypoints.queries.label import QueriesLabel
from kili.orm import Asset
from kili.services import export_labels
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.kili import KiliExporter
from tests.fakes.fake_ffmpeg import mock_ffmpeg
from tests.fakes.fake_kili import (
    FakeKili,
    mocked_AssetQuery,
    mocked_AssetQuery_count,
    mocked_ProjectQuery,
)


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
    "name,test_case",
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
    ],
)
@patch.object(ProjectQuery, "__call__", side_effect=mocked_ProjectQuery)
@patch.object(AssetQuery, "__call__", side_effect=mocked_AssetQuery)
@patch.object(AssetQuery, "count", side_effect=mocked_AssetQuery_count)
@patch("kili.services.export.media.video.ffmpeg")
def test_export_service_layout(
    mocker_ffmpeg, mocker_asset_count, mocker_asset, mocker_project, name, test_case
):
    with TemporaryDirectory() as export_folder:
        with TemporaryDirectory() as extract_folder:
            path_zipfile = Path(export_folder) / "export.zip"
            path_zipfile.parent.mkdir(parents=True, exist_ok=True)

            mock_ffmpeg(mocker_ffmpeg)

            fake_kili = FakeKili()
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
    "name,test_case,error",
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
@patch.object(ProjectQuery, "__call__", side_effect=mocked_ProjectQuery)
@patch.object(AssetQuery, "__call__", side_effect=mocked_AssetQuery)
@patch.object(AssetQuery, "count", side_effect=mocked_AssetQuery_count)
def test_export_service_errors(
    mocker_asset_count, mocker_asset, mocker_project, name, test_case, error
):
    with TemporaryDirectory() as export_folder:
        path_zipfile = Path(export_folder) / "export.zip"
        path_zipfile.parent.mkdir(parents=True, exist_ok=True)

        fake_kili = FakeKili()
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
        }

        default_kwargs.update(test_case["export_kwargs"])
        with pytest.raises(error):
            export_labels(
                fake_kili,  # type: ignore
                **default_kwargs,
            )


def test_export_with_asset_filter_kwargs(mocker):
    get_project_return_val = {"jsonInterface": {}, "inputType": "", "title": ""}
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch.object(KiliExporter, "process_and_save", return_value=None)
    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
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
            "created_at_gte": 0.5,
            "created_at_lte": 0.6,
            "issue_type": "QUESTION",
            "issue_status": None,
            "inference_mark_gte": 0.7,
            "inference_mark_lte": 0.8,
        },
    )

    query_sent = kili.graphql_client.execute.call_args[0][0]
    assert_where = kili.graphql_client.execute.call_args[0][1]["where"]

    assert "query assets($where: AssetWhere!" in query_sent
    assert "data: assets(where: $where" in query_sent

    assert assert_where["project"]["id"] == "fake_proj_id"
    assert assert_where["consensusMarkGte"] == 0.1
    assert assert_where["consensusMarkLte"] == 0.2
    assert assert_where["honeypotMarkGte"] == 0.3
    assert assert_where["honeypotMarkLte"] == 0.4
    assert assert_where["createdAtGte"] == 0.5
    assert assert_where["createdAtLte"] == 0.6
    assert assert_where["inferenceMarkGte"] == 0.7
    assert assert_where["inferenceMarkLte"] == 0.8
    assert assert_where["externalIdStrictlyIn"] == ["truc"]
    assert assert_where["issue"]["type"] == "QUESTION"


def test_export_with_asset_filter_kwargs_unknown_arg(mocker):
    get_project_return_val = {"jsonInterface": {}, "inputType": "", "title": ""}
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch.object(KiliExporter, "_check_arguments_compatibility", return_value=None)
    mocker.patch.object(KiliExporter, "_check_project_compatibility", return_value=None)
    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    with pytest.raises(NameError, match="Unknown asset filter arguments"):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="kili",
            layout="merged",
            with_assets=False,
            asset_filter_kwargs={"this_arg_does_not_exists": 42},
        )


def test_when_exporting_with_assets_given_a_project_with_data_connection_then_it_should_crash(
    mocker,
):
    kili = mock_kili(mocker, with_data_connection=True)
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

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
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    if with_data_connection:
        mocker.patch(
            "kili.services.export.format.base.DataConnectionsQuery.__call__",
            return_value=(i for i in [{"id": "fake_data_connection_id"}]),
        )

    kili = QueriesLabel()
    return kili


def test_when_exporting_without_assets_given_a_project_that_needs_them_it_should_issue_a_warning_and_ensure(
    mocker,
):
    kili = mock_kili(mocker, with_data_connection=False)
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    with pytest.warns(
        UserWarning,
        match=(
            "For an export to this format, the download of assets cannot be disabled,"
            " so they will be downloaded anyway."
        ),
    ):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="coco",
            layout="merged",
            with_assets=False,
        )


def test_convert_to_non_normalized_coords_1(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(KiliExporter, "__init__", return_value=None)
    exporter = KiliExporter()  # type: ignore  # pylint: disable=no-value-for-parameter
    exporter.project = {
        "inputType": "PDF",
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
                    "instruction": "BB",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                }
            }
        },
    }
    asset = {
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
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ]
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ]
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "content": "",
                            "mid": "20230703112327217-43948",
                            "type": "rectangle",
                        },
                    ]
                }
            },
            "createdAt": "2023-07-03T12:18:08.825Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"pageNumber": 1, "height": 842, "width": 595, "rotation": 0},
            {"pageNumber": 2, "height": 842, "width": 595, "rotation": 0},
        ],
    }
    scaled_asset = exporter.convert_to_pixel_coords(asset)  # type: ignore

    assert scaled_asset == {
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
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ],
                                            "vertices": [
                                                {"x": 0.47 * 595, "y": 0.1 * 842},
                                                {"x": 0.47 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.1 * 842},
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ],
                                            "vertices": [
                                                {"x": 0.47 * 595, "y": 0.1 * 842},
                                                {"x": 0.47 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.1 * 842},
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "content": "",
                            "mid": "20230703112327217-43948",
                            "type": "rectangle",
                        },
                    ]
                }
            },
            "createdAt": "2023-07-03T12:18:08.825Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"pageNumber": 1, "height": 842, "width": 595, "rotation": 0},
            {"pageNumber": 2, "height": 842, "width": 595, "rotation": 0},
        ],
    }


def test_convert_to_non_normalized_coords_2(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "inputType": "PDF",
        "id": "fake_proj_id",
        "title": "fake_proj_title",
        "description": "fake_proj_description",
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
                    "instruction": "BBox",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                },
                "CLASSIFICATION_JOB": {
                    "content": {
                        "categories": {
                            "C": {"children": [], "name": "C"},
                            "D": {"children": [], "name": "D"},
                        },
                        "input": "radio",
                    },
                    "instruction": "Class",
                    "mlTask": "CLASSIFICATION",
                    "required": 1,
                    "isChild": False,
                },
            }
        },
    }
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch("kili.entrypoints.queries.label.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            Asset(asset)
            for asset in json.load(open("./tests/services/export/fakes/pdf_project_assets.json"))
        ],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    kili.export_labels(
        "fake_proj_id", "export_pixel_coords_kili_pdf.zip", fmt="kili", normalized_coordinates=False
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_pixel_coords_kili_pdf.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()
        assert Path(f"{extract_folder}/labels").is_dir()
        assert Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").is_file()

        with Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").open() as f:
            output = json.load(f)

    assert output == {
        "content": "https://storage.googleapis.com/label-backend-staging/projects/cljo5b3jjd31f9k8blj7/assets/cljo5b4dcf",
        "externalId": "Cas technique n9.pdf",
        "id": "cljo5b42500042a6akiuy79o7",
        "jsonContent": "",
        "jsonMetadata": {},
        "latestLabel": {
            "author": {
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "id": "user-feat1-1",
                "lastname": "Test Admin",
            },
            "createdAt": "2023-07-04T10:40:52.065Z",
            "isLatestLabelForUser": True,
            "jsonResponse": {
                "CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "C"}]},
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.009304248327663437,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.009304248327663437,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.009304248327663437,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.009304248327663437,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124040213-29399",
                        },
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.831179517271267,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.831179517271267,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.831179517271267,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.831179517271267,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "B"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124043531-11579",
                        },
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.13165433196683027,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.13165433196683027,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [2],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.13165433196683027,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.13165433196683027,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "B"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124045705-1891",
                        },
                    ]
                },
            },
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"height": 842, "pageNumber": 1, "rotation": 0, "width": 595},
            {"height": 595, "pageNumber": 2, "rotation": 0, "width": 420},
        ],
    }
