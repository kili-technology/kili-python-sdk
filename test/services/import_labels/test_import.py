"""
Tests the label import service
"""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from test.services.import_labels.test_cases import TEST_CASES
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest
import yaml

from kili.services import import_labels_from_files
from kili.services.label_import.exceptions import LabelParsingError
from kili.services.label_import.importer import YoloLabelImporter
from kili.services.label_import.parser import YoloLabelParser
from kili.services.label_import.types import Classes
from kili.services.types import ProjectId


def _generate_label_file_list(
    labels_data: List[Dict[str, Any]], filename: str, headers: List[str], annotation_root: str
):
    with Path(filename).open("w", encoding="utf-8") as l_d:
        wrt = csv.writer(l_d)
        wrt.writerow(headers)
        for label_data in labels_data:
            row = []
            for h in headers:
                row.append(
                    label_data[h]
                    if h != "path"
                    else str(Path(annotation_root).joinpath(label_data[h]))
                )
            wrt.writerow(row)


def _generate_label_file(yolo_rows: List[List], filename: str):
    with Path(filename).open("w", encoding="utf-8") as y_f:
        wrt = csv.writer(y_f, delimiter=" ")
        wrt.writerows((str(a) for a in r) for r in yolo_rows)


def _generate_meta_file(yolo_classes, yolo_meta_path, input_format):
    if input_format == "yolo_v4":
        with open(yolo_meta_path, "w", encoding="utf-8") as y_m:
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
def test_import_labels_from_files(description, inputs, outputs):

    kili = MagicMock()
    kili.append_to_labels = MagicMock()

    with TemporaryDirectory() as label_folders:
        yolo_all_labels_path = Path(label_folders) / inputs["label_csv_path"]
        for rows in inputs["labels"]["rows"]:
            yolo_label_path = Path(label_folders) / rows["path"]
            yolo_rows = rows["yolo_data"]
            _generate_label_file(yolo_rows, str(yolo_label_path))

        yolo_classes = inputs["yolo_classes"]
        yolo_meta_path = Path(label_folders) / inputs["meta_path"]

        _generate_meta_file(yolo_classes, yolo_meta_path, inputs["label_format"])

        _generate_label_file_list(
            inputs["labels"]["rows"],
            str(yolo_all_labels_path),
            headers=inputs["labels"]["headers"],
            annotation_root=label_folders,
        )

        import_labels_from_files(
            kili,
            str(yolo_all_labels_path),
            None,
            str(yolo_meta_path),
            ProjectId(inputs["project_id"]),
            inputs["label_format"],
            inputs["target_job_name"],
            disable_tqdm=False,
            log_level="INFO",
            is_prediction=False,
            model_name=None,
        )

        for row in outputs["calls"]:
            kili.append_to_labels.assert_called_with(**row)


def test_import_labels_from_files_malformed_annotation():

    kili = MagicMock()
    kili.append_to_labels = MagicMock()

    inputs = {
        "label_csv_path": "labels.csv",
        "labels": {
            "rows": [
                {
                    "yolo_data": "This is not yolo data...",
                    "label_asset_external_id": "aieaie",
                    "path": "label1.txt",
                },
            ],
            "path": "wrong_annotation.json",
            "headers": ["label_asset_external_id", "path"],
        },
        "meta_path": "classes.txt",
        "yolo_classes": ["A", "B"],
        "project_id": "pid1",
        "target_job_name": "Job1",
    }

    with TemporaryDirectory() as label_folders:
        yolo_all_labels_path = Path(label_folders) / inputs["label_csv_path"]
        for rows in inputs["labels"]["rows"]:
            yolo_label_path = Path(label_folders) / rows["path"]
            yolo_rows = rows["yolo_data"]
            _generate_label_file(yolo_rows, str(yolo_label_path))

        yolo_classes = inputs["yolo_classes"]
        yolo_meta_path = Path(label_folders) / inputs["meta_path"]

        with open(yolo_meta_path, "w", encoding="utf-8") as y_m:
            wrt = csv.writer(y_m, delimiter=" ")
            wrt.writerows((str(a) for a in r) for r in yolo_classes)

        _generate_label_file_list(
            inputs["labels"]["rows"],
            str(yolo_all_labels_path),
            headers=inputs["labels"]["headers"],
            annotation_root=label_folders,
        )

        with pytest.raises(LabelParsingError):
            import_labels_from_files(
                kili,
                str(yolo_all_labels_path),
                None,
                str(yolo_meta_path),
                ProjectId(inputs["project_id"]),
                "yolo_v4",
                inputs["target_job_name"],
                disable_tqdm=False,
                log_level="INFO",
                is_prediction=False,
                model_name=None,
            )


def test__read_labels_file_path():
    author_id = "Jean-Pierre"
    asset_external_id = "un_asset"
    asset_id = None
    type_ = "DEFAULT"
    seconds_to_label = 0

    with TemporaryDirectory() as label_folders:
        yolo_all_label_paths = Path(label_folders) / "yolo.csv"
        yolo_one_label = Path(label_folders) / "one_label.txt"
        o_l = yolo_one_label.open("w", encoding="utf-8")
        o_l.close()
        annotation_file_row = {
            "path": yolo_one_label,
            "author_id": author_id,
            "label_asset_external_id": asset_external_id,
            "label_asset_id": asset_id,
            "label_type": type_,
            "seconds_to_label": seconds_to_label,
        }
        _generate_label_file_list(
            [annotation_file_row],
            str(yolo_all_label_paths),
            [
                "path",
                "author_id",
                "label_asset_external_id",
                "label_asset_id",
                "label_type",
                "seconds_to_label",
            ],
            label_folders,
        )
        labels_to_import = (
            YoloLabelImporter._read_labels_file_path(  # pylint: disable=protected-access
                yolo_all_label_paths
            )
        )
        assert len(labels_to_import) == 1
        assert labels_to_import[0]["author_id"] == author_id
        assert labels_to_import[0]["label_asset_external_id"] == asset_external_id
        assert "label_asset_id" not in labels_to_import[0]
        assert labels_to_import[0]["label_type"] == type_
        assert labels_to_import[0]["seconds_to_label"] == seconds_to_label
        assert labels_to_import[0]["path"] == str(yolo_one_label)


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
