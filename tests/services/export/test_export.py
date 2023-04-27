# pylint: disable=missing-module-docstring
import glob
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.entrypoints.queries.label import QueriesLabel
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
            }

            default_kwargs.update(test_case["export_kwargs"])

            export_labels(
                fake_kili.auth,  # type: ignore
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
        }

        default_kwargs.update(test_case["export_kwargs"])
        with pytest.raises(error):
            export_labels(
                fake_kili.auth,  # type: ignore
                **default_kwargs,
            )


def test_export_with_asset_filter_kwargs(mocker):
    get_project_return_val = {"jsonInterface": {}, "inputType": "", "title": ""}
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch.object(KiliExporter, "process_and_save", return_value=None)
    mocker_auth = mocker.MagicMock()
    kili = QueriesLabel(auth=mocker_auth)
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

    query_sent = mocker_auth.client.execute.call_args[0][0]
    assert_where = mocker_auth.client.execute.call_args[0][1]["where"]

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
    kili = QueriesLabel(auth=mocker.MagicMock())

    with pytest.raises(NameError, match="Unknown asset filter arguments"):
        kili.export_labels(
            project_id="fake_proj_id",
            filename="fake_filename",
            fmt="kili",
            layout="merged",
            with_assets=False,
            asset_filter_kwargs={"this_arg_does_not_exists": 42},
        )


def test_export_with_asset_cloud_storage_should_crash(mocker):
    get_project_return_val = {
        "jsonInterface": {"jobs": {"JOB": {"tools": ["rectangle"], "mlTask": "OBJECT_DETECTION"}}},
        "inputType": "IMAGE",
        "title": "",
    }
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch.object(KiliExporter, "_check_arguments_compatibility", return_value=None)
    mocker.patch.object(KiliExporter, "_check_project_compatibility", return_value=None)
    mocker.patch(
        "kili.services.export.format.base.DataConnectionsQuery.__call__",
        return_value=(i for i in [{"id": "fake_data_connection_id"}]),
    )

    kili = QueriesLabel(auth=mocker.MagicMock())

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
            fmt="pascal_voc",
            layout="merged",
            with_assets=True,
        )
