"""
Tests the label import service
"""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List
from unittest.mock import MagicMock, patch

import pytest
import yaml

from kili.exceptions import NotFound
from kili.graphql.operations.project.queries import ProjectQuery
from kili.services import import_labels_from_files
from kili.services.label_import.exceptions import LabelParsingError
from kili.services.label_import.importer import YoloLabelImporter
from kili.services.label_import.parser import YoloLabelParser
from kili.services.label_import.types import Classes
from kili.services.types import ProjectId
from tests.services.import_labels import fakes
from tests.services.import_labels.test_cases_from_files import TEST_CASES


def _generate_label_file(yolo_rows: List[List], filename: str):
    # newline="" to disable universal newlines translation (bug fix for windows)
    with Path(filename).open("w", newline="", encoding="utf-8") as y_f:
        wrt = csv.writer(y_f, delimiter=" ")
        wrt.writerows((str(a) for a in r) for r in yolo_rows)


def _generate_meta_file(yolo_classes, yolo_meta_path, input_format):
    if input_format == "yolo_v4":
        # newline="" to disable universal newlines translation (bug fix for windows)
        with open(yolo_meta_path, "w", newline="", encoding="utf-8") as y_m:
            wrt = csv.writer(y_m, delimiter=" ")
            wrt.writerows((str(a) for a in r) for r in yolo_classes)
    elif input_format == "yolo_v5":
        with open(yolo_meta_path, "w", encoding="utf-8") as y_m:
            y_m.write(yaml.dump({"names": dict(yolo_classes)}))
    elif input_format == "yolo_v7":
        with open(yolo_meta_path, "w", encoding="utf-8") as y_m:
            y_m.write(yaml.dump({"nc": len(yolo_classes), "names": [c[1] for c in yolo_classes]}))
    else:
        raise NotImplementedError(f"Format {input_format} not implemented yet")


@pytest.mark.parametrize(
    "description,inputs,outputs",
    [
        (test_case["description"], test_case["inputs"], test_case["outputs"])
        for test_case in TEST_CASES
    ],
)
@patch.object(ProjectQuery, "__call__", side_effect=fakes.projects)
def test_import_labels_from_files(mocker, description, inputs, outputs):
    auth = MagicMock()

    with TemporaryDirectory() as label_folders:
        label_paths = []
        for label in inputs["labels"]:
            yolo_label_path = Path(label_folders) / label["path"]
            label_paths.append(yolo_label_path)
            yolo_rows = label["yolo_data"]
            _generate_label_file(yolo_rows, str(yolo_label_path))

        yolo_classes = inputs["yolo_classes"]
        yolo_meta_path = Path(label_folders) / inputs["meta_path"]

        _generate_meta_file(yolo_classes, yolo_meta_path, inputs["label_format"])

        with patch(
            "kili.services.label_import.importer.AbstractLabelImporter.process_from_dict"
        ) as process_from_dict_mock:
            import_labels_from_files(
                auth,
                label_paths,
                str(yolo_meta_path),
                ProjectId(inputs["project_id"]),
                inputs["label_format"],
                inputs["target_job_name"],
                disable_tqdm=False,
                log_level="INFO",
                model_name=None,
                is_prediction=False,
            )

            process_from_dict_mock.assert_called_with(**outputs["call"])


@patch.object(ProjectQuery, "__call__", side_effect=fakes.projects)
def test_import_labels_from_files_malformed_annotation(mocker):
    auth = MagicMock()

    inputs = {
        "labels": [
            {
                "yolo_data": "This is not yolo data...",
                "path": "aieaie.txt",
            }
        ],
        "path": "wrong_annotation.json",
        "meta_path": "classes.txt",
        "yolo_classes": ["A", "B"],
        "project_id": "pid1",
        "target_job_name": "Job1",
    }

    with TemporaryDirectory() as label_folders:
        label_paths = []
        for label in inputs["labels"]:
            yolo_label_path = Path(label_folders) / label["path"]
            label_paths.append(yolo_label_path)
            yolo_rows = label["yolo_data"]
            _generate_label_file(yolo_rows, str(yolo_label_path))

        yolo_classes = inputs["yolo_classes"]
        yolo_meta_path = Path(label_folders) / inputs["meta_path"]

        # newline="" to disable universal newlines translation (bug fix for windows)
        with open(yolo_meta_path, "w", newline="", encoding="utf-8") as y_m:
            wrt = csv.writer(y_m, delimiter=" ")
            wrt.writerows((str(a) for a in r) for r in yolo_classes)

        with pytest.raises(LabelParsingError):
            import_labels_from_files(
                auth,
                label_paths,
                str(yolo_meta_path),
                ProjectId(inputs["project_id"]),
                "yolo_v4",
                inputs["target_job_name"],
                disable_tqdm=False,
                log_level="INFO",
                is_prediction=False,
                model_name=None,
            )


@patch.object(ProjectQuery, "__call__", side_effect=fakes.projects)
def test_import_labels_wrong_target_job(mocker):
    auth = MagicMock()

    inputs = {
        "labels": [
            {
                "yolo_data": [],
                "path": "un_asset.txt",
            }
        ],
        "project_id": "yolo!",
        "target_job_name": "JOB_1",
        "meta_path": "yolo_classes.txt",
        "yolo_classes": [[0, "A"], [1, "B"], [2, "C"], [3, "D"]],
        "label_format": "yolo_v4",
    }

    with TemporaryDirectory() as label_folders:
        label_paths = []
        for label in inputs["labels"]:
            yolo_label_path = Path(label_folders) / label["path"]
            label_paths.append(yolo_label_path)
            yolo_rows = label["yolo_data"]
            _generate_label_file(yolo_rows, str(yolo_label_path))

        yolo_classes = inputs["yolo_classes"]
        yolo_meta_path = Path(label_folders) / inputs["meta_path"]

        # newline="" to disable universal newlines translation (bug fix for windows)
        with open(yolo_meta_path, "w", newline="", encoding="utf-8") as y_m:
            wrt = csv.writer(y_m, delimiter=" ")
            wrt.writerows((str(a) for a in r) for r in yolo_classes)

        with pytest.raises(NotFound):
            import_labels_from_files(
                auth,
                label_paths,
                str(yolo_meta_path),
                ProjectId(inputs["project_id"]),
                "yolo_v4",
                inputs["target_job_name"],
                disable_tqdm=False,
                log_level="INFO",
                model_name=None,
                is_prediction=False,
            )


@pytest.mark.parametrize(
    "name,filename,lines,label_format, expected",
    [
        (
            "YOLO v4 1st layout",
            "classes.txt",
            ["0 OBJECT_A", "1 OBJECT_B"],
            "yolo_v4",
            {0: "OBJECT_A", 1: "OBJECT_B"},
        ),
        (
            "YOLO v4 2nd layout",
            "classes.txt",
            ["OBJECT A", "OBJECT B"],
            "yolo_v4",
            {0: "OBJECT A", 1: "OBJECT B"},
        ),
        (
            "YOLO v5",
            "data.yaml",
            ["names: ", "  0: OBJECT_A", "  1: OBJECT_B"],
            "yolo_v5",
            {0: "OBJECT_A", 1: "OBJECT_B"},
        ),
        (
            "YOLO v7",
            "data.yaml",
            ["nc: 2", "names: ['OBJECT_A', 'OBJECT_B']"],
            "yolo_v7",
            {0: "OBJECT_A", 1: "OBJECT_B"},
        ),
    ],
)
def test__read_classes_from_meta_file(name, filename, lines, label_format, expected):
    with TemporaryDirectory() as class_dir:
        class_file = Path(class_dir) / filename
        with open(class_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        classes_by_id = (
            YoloLabelImporter._read_classes_from_meta_file(  # pylint: disable=protected-access
                class_file, label_format
            )
        )
        assert classes_by_id == expected


def test_yolo_label_parser():
    with TemporaryDirectory() as label_dir:
        label_file = Path(label_dir) / "label.txt"
        _generate_label_file(
            [
                [1, 0.5, 0.5, 1.0, 1.0],
            ],
            str(label_file),
        )
        yolo_parser = YoloLabelParser(Classes({0: "A", 1: "B", 2: "C", 3: "D"}), "JOB_0")
        expected = {
            "JOB_0": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {
                                "normalizedVertices": [
                                    {"x": 0.0, "y": 0.0},
                                    {"x": 0.0, "y": 1.0},
                                    {"x": 1.0, "y": 1.0},
                                    {"x": 1.0, "y": 0.0},
                                ],
                            }
                        ],
                        "categories": [{"name": "B", "confidence": 100}],
                    }
                ]
            }
        }

        assert expected == yolo_parser.parse(label_file)
