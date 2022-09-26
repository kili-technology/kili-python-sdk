# pylint: disable=missing-docstring
import glob
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from test.services.export.fakes.fake_content_repository import FakeContentRepository
from test.services.export.fakes.fake_data import asset_image, asset_video, category_ids
from test.services.export.fakes.fake_kili import FakeKili
from unittest import TestCase
from zipfile import ZipFile

import pytest

from kili.services import export_labels
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.format.yolo.common import (
    _convert_from_kili_to_yolo_format,
    _process_asset,
    _write_class_file,
)


def get_file_tree(folder: str):
    """
    Returns the file tree in the shape of a dictionary.
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
        for x in f_p.split("/"):
            if len(x):
                p = p.setdefault(x, {})
    return dct


class YoloTestCase(TestCase):
    def test_process_asset_for_job_image_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository("https://contentrep", {}, False)
                asset_remote_content, video_filenames = _process_asset(
                    asset_image, images_folder, labels_folder, category_ids, fake_content_repository
                )

                nb_files = len(
                    [
                        name
                        for name in os.listdir(labels_folder)
                        if os.path.isfile(os.path.join(labels_folder, name))
                    ]
                )

                self.assertTrue(os.path.isfile(os.path.join(labels_folder, "car_1.txt")))
                self.assertEqual(nb_files, 1)
                self.assertEqual(
                    asset_remote_content,
                    [
                        [
                            "car_1",
                            "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                            "car_1.txt",
                        ]
                    ],
                )
                self.assertEqual(len(video_filenames), 0)

    def test_process_asset_for_job_frame_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository("https://contentrep", {}, False)
                asset_remote_content, video_filenames = _process_asset(
                    asset_video, images_folder, labels_folder, category_ids, fake_content_repository
                )

                nb_files = len(
                    [
                        name
                        for name in os.listdir(labels_folder)
                        if os.path.isfile(os.path.join(labels_folder, name))
                    ]
                )

                self.assertEqual(nb_files, 4)

                for i in range(nb_files):
                    self.assertTrue(
                        os.path.isfile(os.path.join(labels_folder, f"video_1_{i+1}.txt"))
                    )

                expected_content = [
                    [
                        "video_1",
                        "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
                        f"video_1_{i+1}.txt",
                    ]
                    for i in range(4)
                ]
                self.assertEqual(asset_remote_content, expected_content)

                expected_video_filenames = [f"video_1_{i+1}" for i in range(4)]
                self.assertEqual(len(video_filenames), 4)
                self.assertEqual(video_filenames, expected_video_filenames)

    def test_convert_from_kili_to_yolo_format(self):
        converted_annotations = _convert_from_kili_to_yolo_format(
            "JOB_0", asset_image["latestLabel"], category_ids
        )
        expected_annotations = [
            (0, 0.501415026274802, 0.5296278884310182, 0.6727472455849373, 0.5381320101586394)
        ]
        self.assertEqual(len(converted_annotations), 1)
        self.assertEqual(converted_annotations, expected_annotations)

    def test_write_class_file_yolo_v4(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v4")
            self.assertTrue(os.path.isfile(os.path.join(directory, "classes.txt")))
            with open(os.path.join(directory, "classes.txt"), "rb") as created_file:
                with open("./test/services/export/expected/classes.txt", "rb") as expected_file:
                    self.assertEqual(expected_file.read(), created_file.read())

    def test_write_class_file_yolo_v5(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v5")
            self.assertTrue(os.path.isfile(os.path.join(directory, "data.yaml")))
            with open(os.path.join(directory, "data.yaml"), "rb") as created_file:
                with open("./test/services/export/expected/data_v5.yaml", "rb") as expected_file:
                    self.assertEqual(expected_file.read(), created_file.read())

    def test_write_class_file_yolo_v7(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v7")
            self.assertTrue(os.path.isfile(os.path.join(directory, "data.yaml")))
            with open(os.path.join(directory, "data.yaml"), "rb") as created_file:
                with open("./test/services/export/expected/data_v7.yaml", "rb") as expected_file:
                    self.assertEqual(expected_file.read(), created_file.read())

    def test_conversion_service(self):
        use_cases = [
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "split",
                },
                "file_tree_expected": {
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
                },
            },
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "data.yaml": {},
                    "README.kili.txt": {},
                },
            },
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "classes.txt": {},
                    "README.kili.txt": {},
                },
            },
        ]

        for use_case in use_cases:
            with TemporaryDirectory() as export_folder:
                with TemporaryDirectory() as extract_folder:
                    path_zipfile = Path(export_folder) / "export.zip"
                    path_zipfile.parent.mkdir(parents=True, exist_ok=True)

                    fake_kili = FakeKili()
                    default_kwargs = {
                        "asset_ids": [],
                        "split_option": "merged",
                        "export_type": "latest",
                        "output_file": str(path_zipfile),
                        "disable_tqdm": True,
                        "log_level": "INFO",
                    }

                    default_kwargs.update(use_case["export_kwargs"])

                    export_labels(
                        fake_kili,
                        **default_kwargs,
                    )

                    Path(extract_folder).mkdir(parents=True, exist_ok=True)
                    with ZipFile(path_zipfile, "r") as z_f:
                        z_f.extractall(extract_folder)

                    file_tree_result = get_file_tree(extract_folder)

                    file_tree_expected = use_case["file_tree_expected"]

                    assert file_tree_result == file_tree_expected

    def test_conversion_service_errors(self):
        use_cases = [
            {
                "export_kwargs": {
                    "project_id": "text_classification",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                },
            }
        ]

        for use_case in use_cases:
            with TemporaryDirectory() as export_folder:
                path_zipfile = Path(export_folder) / "export.zip"
                path_zipfile.parent.mkdir(parents=True, exist_ok=True)

                fake_kili = FakeKili()
                default_kwargs = {
                    "asset_ids": [],
                    "split_option": "merged",
                    "export_type": "latest",
                    "output_file": str(path_zipfile),
                    "disable_tqdm": True,
                    "log_level": "INFO",
                }

                default_kwargs.update(use_case["export_kwargs"])
                with pytest.raises(NoCompatibleJobError):
                    export_labels(
                        fake_kili,
                        **default_kwargs,
                    )
