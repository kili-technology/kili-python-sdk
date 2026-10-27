# pylint: disable=missing-docstring

import copy
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

import pytest
import pytest_mock
from kili_formats import convert_from_kili_to_yolo_format
from kili_formats.layout import YoloFolder, yolo_class_file

from kili.adapters.http_client import HttpClient
from kili.presentation.client.label import LabelClientMethods
from kili.services.export import YoloExporter
from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.format.yolo import YoloExporter, _write_labels_to_file
from kili.utils.tempfile import TemporaryDirectory
from tests.fakes.fake_data import (
    asset_image_1,
    asset_image_1_with_0_rotation,
    asset_image_1_with_90_rotation,
    asset_image_1_with_180_rotation,
    asset_image_1_with_270_rotation,
    asset_image_1_without_annotation,
    asset_video,
    category_ids,
)
from tests.unit.services.export.fakes.fake_content_repository import (
    FakeContentRepository,
)


def _write_asset(asset: dict, input_type: str, repository, export_root: Path):
    """An exporter's `_write_asset`, without the assets, its detect folder at the root.

    Return the remote rows, the video's frames and the labels folder.
    """
    exporter = YoloExporter.__new__(YoloExporter)
    exporter.project = {
        "inputType": input_type,
        "jsonInterface": {
            "jobs": {"JOB_0": {"mlTask": "OBJECT_DETECTION", "tools": ["rectangle"]}}
        },
    }
    exporter.project_id = "project"  # type: ignore
    exporter.export_root_folder = export_root  # type: ignore
    exporter.folders = {"": YoloFolder("detect", category_ids)}
    exporter.with_assets = False
    exporter.content_repository = repository
    rows, frames_by_folder, _images = exporter._write_asset(asset)  # pylint: disable=protected-access
    return rows, frames_by_folder[""], Path(export_root) / "project" / "labels"


def _classes(*names: str, in_folder: bool = False) -> str:
    """A data.yaml: its images, the shared ones above a task's or a job's folder, and its classes."""
    images = "../images" if in_folder else "images"
    quoted = ", ".join(f'"{name}"' for name in names)
    return f"train: {images}\nval: {images}\nnc: {len(names)}\nnames: [{quoted}]\n"


def test_process_asset_for_job_image_not_served_by_kili():
    with TemporaryDirectory() as images_folder, TemporaryDirectory() as labels_folder:
        fake_content_repository = FakeContentRepository(
            "https://contentrep",
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com",
                api_key="",
                verify=True,
            ),
        )
        asset_remote_content, video_filenames, labels_folder = _write_asset(
            {
                "latestLabel": {
                    "jsonResponse": {
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
                    },
                    "author": {"firstname": "Jean-Pierre", "lastname": "Dupont"},
                },
                "externalId": "car_1",
                "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "jsonContent": "",
                "resolution": {"height": 1000, "width": 1000},
            },
            "IMAGE",
            fake_content_repository,
            labels_folder,
        )

        nb_files = len(
            [name for name in labels_folder.iterdir() if (labels_folder / name).is_file()]
        )

        assert (labels_folder / "car_1.txt").is_file()
        assert nb_files == 1
        assert asset_remote_content == [
            (
                "car_1",
                "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "car_1.txt",
            )
        ]
        assert len(video_filenames) == 0


def test_process_asset_for_job_frame_not_served_by_kili():
    with TemporaryDirectory() as images_folder, TemporaryDirectory() as labels_folder:
        fake_content_repository = FakeContentRepository(
            "https://contentrep",
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com",
                api_key="",
                verify=True,
            ),
        )
        asset_remote_content, video_filenames, labels_folder = _write_asset(
            asset_video,
            "VIDEO",
            fake_content_repository,
            labels_folder,
        )

        nb_files = len(
            [name for name in labels_folder.iterdir() if (labels_folder / name).is_file()]
        )

        assert nb_files == 4

        for i in range(nb_files):
            assert (labels_folder / f"video_1_{i+1}.txt").is_file()

        expected_content = [
            (
                "video_1",
                "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
                f"video_1_{i+1}.txt",
            )
            for i in range(4)
        ]
        assert asset_remote_content == expected_content

        expected_video_filenames = [f"video_1_{i+1}" for i in range(4)]
        assert len(video_filenames) == 4
        assert video_filenames == expected_video_filenames


class _FramesRepository(FakeContentRepository):
    """Serves a 130-frame video's frames json."""

    def get_frames(self, content_url: str) -> list[str]:
        assert content_url == "https://storage.example/clip.json"
        return [f"https://storage.example/clip-{i + 1:03d}.jpg" for i in range(130)]


def test_a_frame_video_not_downloaded_lists_its_frames_named_after_the_video():
    box = {
        "categories": [{"name": "OBJECT_A"}],
        "type": "rectangle",
        "boundingPoly": [
            {
                "normalizedVertices": [
                    {"x": 0.1, "y": 0.1},
                    {"x": 0.1, "y": 0.2},
                    {"x": 0.2, "y": 0.2},
                ]
            }
        ],
    }
    asset = {
        "externalId": "clip",
        "content": "https://storage.example/clip.mp4",
        "jsonContent": "https://storage.example/clip.json",
        "latestLabel": {
            "jsonResponse": {
                str(i): ({"JOB_0": {"annotations": [box]}} if i in (2, 11) else {})
                for i in range(15)
            }
        },
    }
    repository = _FramesRepository(
        "https://contentrep",
        HttpClient(
            kili_endpoint="https://fake_endpoint.kili-technology.com", api_key="", verify=True
        ),
    )
    with TemporaryDirectory() as export_root:
        rows, frames, labels_folder = _write_asset(asset, "VIDEO", repository, export_root)

        # Padded to the video's 130 frames, not the label's 15, as the app names them
        assert sorted(path.name for path in labels_folder.iterdir()) == [
            "clip_003.txt",
            "clip_012.txt",
        ]
    assert frames == ["clip_003", "clip_012"]
    assert rows == [
        ("clip", "https://storage.example/clip-003.jpg", "clip_003.txt"),
        ("clip", "https://storage.example/clip-012.jpg", "clip_012.txt"),
    ]


def test_convert_from_kili_to_yolo_format():
    converted_annotations = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1["latestLabel"], category_ids
    )
    converted_annotations_with_rotation_0 = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1_with_0_rotation["latestLabel"], category_ids
    )
    converted_annotations_with_rotation_90 = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1_with_90_rotation["latestLabel"], category_ids
    )
    converted_annotations_with_rotation_180 = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1_with_180_rotation["latestLabel"], category_ids
    )
    converted_annotations_with_rotation_270 = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1_with_270_rotation["latestLabel"], category_ids
    )
    expected_annotations1 = [
        (0, 0.501415026274802, 0.5296278884310182, 0.6727472455849373, 0.5381320101586394)
    ]
    expected_annotations2 = [
        (0, 0.20836785418392711, 0.28447691496573013, 0.2609776304888154, 0.3803570083603225)
    ]
    assert len(converted_annotations) == 1
    assert converted_annotations == expected_annotations1
    assert len(converted_annotations_with_rotation_0) == 1
    assert converted_annotations_with_rotation_0 == expected_annotations2
    assert len(converted_annotations_with_rotation_90) == 1
    assert converted_annotations_with_rotation_90 == expected_annotations2
    assert len(converted_annotations_with_rotation_180) == 1
    assert converted_annotations_with_rotation_180 == expected_annotations2
    assert len(converted_annotations_with_rotation_270) == 1
    assert converted_annotations_with_rotation_270 == expected_annotations2


def test_convert_from_kili_to_yolo_format_no_annotation():
    converted_annotations = convert_from_kili_to_yolo_format(
        "JOB_0", asset_image_1_without_annotation["latestLabel"], category_ids
    )
    assert len(converted_annotations) == 0


@pytest.mark.parametrize(
    ("fmt", "class_file", "expected"),
    [
        ("yolo_v4", "classes.txt", "classes.txt"),
        ("yolo_v5", "data.yaml", "data_v5.yaml"),
        ("yolo_v7", "data.yaml", "data_v7.yaml"),
    ],
)
def test_write_class_file(fmt: str, class_file: str, expected: str):
    folder = YoloFolder("detect", category_ids, with_job=False)

    with open(f"./tests/unit/services/export/expected/{expected}") as expected_file:
        assert yolo_class_file(folder, fmt) == (class_file, expected_file.read())  # type: ignore


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


def _export(
    mocker: pytest_mock.MockerFixture,
    extract_folder: Path,
    fmt: str = "yolo_v8",
    layout: str = "merged",
    jobs: Optional[list[str]] = None,
    remote: bool = False,
    bbox_as: str = "box",
) -> Optional[Path]:
    """Export the project, its interface down to `jobs` when given, and extract the archive.

    The image is served by Kili, unless `remote`: then the export lists it in remote_assets.csv.
    No archive, None.
    """
    project = copy.deepcopy(get_project_return_val)
    if jobs is not None:
        project["jsonInterface"]["jobs"] = {
            job_id: project["jsonInterface"]["jobs"][job_id] for job_id in jobs
        }
    mocker.patch(
        "kili.services.export.format.base.fetch_assets", return_value=copy.deepcopy(assets)
    )
    mocker.patch.object(YoloExporter, "_has_data_connection", return_value=False)
    if remote:
        mocker.patch(
            "kili.services.export.repository.AbstractContentRepository.is_serving",
            return_value=False,
        )

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = project
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / f"export_{fmt}.zip")
        kili.export_labels(
            "clktm4vzz001a0j324elr5dsy",
            filename=export_filename,
            fmt=fmt,  # type: ignore
            layout=layout,  # type: ignore
            with_assets=False,
            bbox_as=bbox_as,  # type: ignore
        )
        if not Path(export_filename).is_file():
            return None
        with ZipFile(export_filename, "r") as z_f:
            z_f.extractall(extract_folder)
    return extract_folder


BOX_LINE = "0 0.65 0.1 0.5 0.09999999999999999\n"
# the box as its four corners: class x1 y1 x2 y2 x3 y3 x4 y4
BOX_AS_POLYGON = "0 0.4 0.15 0.4 0.05 0.9 0.05 0.9 0.15"
POLYGON = "0.75 0.23 0.35 0.22 0.07 0.35"


def test_yolo_v8_writes_a_detect_and_a_segment_dataset_on_box_and_polygon_jobs(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path)
    assert folder is not None
    assert folder

    assert (folder / "README.kili.txt").is_file()
    assert (folder / "detect" / "data.yaml").read_text() == _classes(
        "OBJECT_DETECTION_JOB/A", "OBJECT_DETECTION_JOB/B", in_folder=True
    )
    assert (folder / "detect" / "labels" / "trees.txt").read_text() == BOX_LINE
    # The boxes are in detect alone
    assert (folder / "segment" / "data.yaml").read_text() == _classes(
        "POLYGON_JOB/F", "POLYGON_JOB/G", in_folder=True
    )
    assert (folder / "segment" / "labels" / "trees.txt").read_text() == f"0 {POLYGON}\n"
    assert not (folder / "labels").exists()
    assert not (folder / "data.yaml").exists()


def test_yolo_v8_writes_an_obb_and_a_segment_dataset_when_boxes_are_oriented(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, bbox_as="obb")
    assert folder is not None

    assert (folder / "obb" / "data.yaml").read_text() == _classes(
        "OBJECT_DETECTION_JOB/A", "OBJECT_DETECTION_JOB/B", in_folder=True
    )
    assert (folder / "obb" / "labels" / "trees.txt").read_text() == f"{BOX_AS_POLYGON}\n"
    assert (folder / "segment" / "labels" / "trees.txt").read_text() == f"0 {POLYGON}\n"
    assert not (folder / "detect").exists()


def test_yolo_v8_writes_one_segment_dataset_when_boxes_are_polygons(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, bbox_as="polygon")
    assert folder is not None

    assert (folder / "data.yaml").read_text() == _classes(
        "OBJECT_DETECTION_JOB/A", "OBJECT_DETECTION_JOB/B", "POLYGON_JOB/F", "POLYGON_JOB/G"
    )
    label = (folder / "labels" / "trees.txt").read_text()
    assert BOX_AS_POLYGON in label
    assert f"2 {POLYGON}" in label
    assert not (folder / "detect").exists()
    assert not (folder / "segment").exists()


def test_yolo_v8_split_writes_the_box_job_for_the_boxes_task(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, layout="split", bbox_as="obb")
    assert folder is not None

    assert (
        folder / "OBJECT_DETECTION_JOB" / "labels" / "trees.txt"
    ).read_text() == f"{BOX_AS_POLYGON}\n"
    assert (folder / "POLYGON_JOB" / "labels" / "trees.txt").read_text() == f"0 {POLYGON}\n"


@pytest.mark.parametrize("fmt", ["yolo_v4", "coco", "pascal_voc", "kili"])
def test_bbox_as_is_for_the_ultralytics_yolo_formats_only(
    mocker: pytest_mock.MockerFixture, tmp_path: Path, fmt: str
):
    with pytest.raises(NotCompatibleOptions, match='bbox_as="obb"'):
        _export(mocker, tmp_path, fmt=fmt, bbox_as="obb")


def test_yolo_v8_lists_a_remote_image_once_for_both_datasets(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, remote=True)
    assert folder is not None

    remote_assets = (folder / "images" / "remote_assets.csv").read_text().splitlines()
    assert remote_assets == ["external id,url,label file", "trees,https://sdf,trees.txt"]


def test_yolo_v8_split_writes_a_folder_per_job_for_its_own_task(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, layout="split")
    assert folder is not None

    assert (folder / "OBJECT_DETECTION_JOB" / "data.yaml").read_text() == _classes(
        "A", "B", in_folder=True
    )
    # the box job: detect
    assert (folder / "OBJECT_DETECTION_JOB" / "labels" / "trees.txt").read_text() == BOX_LINE
    assert (folder / "POLYGON_JOB" / "data.yaml").read_text() == _classes("F", "G", in_folder=True)
    # the polygon job: segment
    assert (folder / "POLYGON_JOB" / "labels" / "trees.txt").read_text() == f"0 {POLYGON}\n"
    assert not (folder / "detect").exists()
    assert not (folder / "segment").exists()


def test_yolo_v8_writes_the_detect_dataset_at_the_root_on_box_jobs_alone(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, jobs=["OBJECT_DETECTION_JOB"])
    assert folder is not None

    assert (folder / "data.yaml").read_text() == _classes(
        "OBJECT_DETECTION_JOB/A", "OBJECT_DETECTION_JOB/B"
    )
    assert (folder / "labels" / "trees.txt").read_text() == BOX_LINE
    assert not (folder / "detect").exists()
    assert not (folder / "segment").exists()


def test_yolo_v8_writes_the_segment_dataset_at_the_root_on_polygon_jobs_alone(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, jobs=["POLYGON_JOB"])
    assert folder is not None

    assert (folder / "data.yaml").read_text() == _classes("POLYGON_JOB/F", "POLYGON_JOB/G")
    assert (folder / "labels" / "trees.txt").read_text() == f"0 {POLYGON}\n"
    assert not (folder / "segment").exists()


def test_yolo_v4_writes_the_detect_dataset_alone_at_the_root(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    folder = _export(mocker, tmp_path, fmt="yolo_v4")
    assert folder is not None

    assert (folder / "classes.txt").read_text() == (
        "0 OBJECT_DETECTION_JOB/A\n1 OBJECT_DETECTION_JOB/B\n"
    )
    assert (folder / "labels" / "trees.txt").read_text() == BOX_LINE
    assert not (folder / "segment").exists()


def test_yolo_v4_refuses_a_project_with_polygon_jobs_alone(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    with pytest.warns(UserWarning, match="at least one compatible job"):
        assert _export(mocker, tmp_path, fmt="yolo_v4", jobs=["POLYGON_JOB"]) is None


def test_write_labels_to_file_with_external_id_containing_slash(tmp_path: Path):
    _write_labels_to_file(tmp_path, "image/1.txt", "0 0.5 0.5 0.6 0.5\n")

    assert (tmp_path / "image" / "1.txt").is_file()


def test_process_asset_with_latest_labels():
    """Test that multiple labels create separate annotation files with label suffix."""
    with TemporaryDirectory() as images_folder, TemporaryDirectory() as labels_folder:
        fake_content_repository = FakeContentRepository(
            "https://contentrep",
            HttpClient(
                kili_endpoint="https://fake_endpoint.kili-technology.com",
                api_key="",
                verify=True,
            ),
        )
        asset_remote_content, video_filenames, labels_folder = _write_asset(
            {
                "latestLabels": [
                    {
                        "jsonResponse": {
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
                                                    {"x": 0.1, "y": 0.8},
                                                    {"x": 0.1, "y": 0.2},
                                                    {"x": 0.8, "y": 0.2},
                                                    {"x": 0.8, "y": 0.8},
                                                ]
                                            }
                                        ],
                                        "type": "rectangle",
                                        "children": {},
                                    }
                                ]
                            }
                        },
                        "author": {"firstname": "User", "lastname": "One"},
                    },
                    {
                        "jsonResponse": {
                            "JOB_0": {
                                "annotations": [
                                    {
                                        "categories": [{"confidence": 100, "name": "OBJECT_B"}],
                                        "jobName": "JOB_0",
                                        "mid": "2022040515434712-7533",
                                        "mlTask": "OBJECT_DETECTION",
                                        "boundingPoly": [
                                            {
                                                "normalizedVertices": [
                                                    {"x": 0.2, "y": 0.9},
                                                    {"x": 0.2, "y": 0.3},
                                                    {"x": 0.9, "y": 0.3},
                                                    {"x": 0.9, "y": 0.9},
                                                ]
                                            }
                                        ],
                                        "type": "rectangle",
                                        "children": {},
                                    }
                                ]
                            }
                        },
                        "author": {"firstname": "User", "lastname": "Two"},
                    },
                ],
                "externalId": "multi_label",
                "content": "https://storage.googleapis.com/label-public-staging/car/multi.jpg",
                "jsonContent": "",
                "resolution": {"height": 1000, "width": 1000},
            },
            "IMAGE",
            fake_content_repository,
            labels_folder,
        )

        # Should create two label files with suffixes
        assert (labels_folder / "multi_label_label1.txt").is_file()
        assert (labels_folder / "multi_label_label2.txt").is_file()
        assert len(asset_remote_content) == 2
        assert len(video_filenames) == 0
