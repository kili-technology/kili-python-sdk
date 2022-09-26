import csv
import json
import os
from unittest.mock import ANY, MagicMock, patch

import pytest
from click.testing import CliRunner

from kili.cli.project.label import import_labels

from ...utils import debug_subprocess_pytest
from .mocks.projects import mocked__projects

kili_client = MagicMock()
kili_client.projects = project_mock = MagicMock(side_effect=mocked__projects)
kili_client.create_predictions = create_predictions_mock = MagicMock()

mock_label = {"JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}}


@patch("kili.client.Kili.__new__", return_value=kili_client)
class TestCLIProjectImport:
    @pytest.mark.parametrize(
        "name,test_case",
        [
            (
                "AAU, when I import a list of label's file to project, I see a success",
                {
                    "files": [
                        "test_tree/leaf_1/",
                        "test_tree/asset1.json",
                        "test_tree/leaf_2/**.json",
                    ],
                    "options": {
                        "project-id": "project_id",
                    },
                    "flags": [],
                    "mutation_to_call": "append_to_labels",
                    "expected_mutation_payload": {
                        "project_id": "project_id",
                        "json_response": {
                            "JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}
                        },
                        "label_asset_external_id": "asset6",
                    },
                    "expected_mutation_call_count": 5,
                },
            ),
            (
                "AAU, when I import default labels from a CSV, I see a success",
                {
                    "files": [],
                    "options": {
                        "project-id": "project_id",
                        "from-csv": "labels_to_import.csv",
                    },
                    "flags": [],
                    "mutation_to_call": "append_to_labels",
                    "expected_mutation_payload": {
                        "project_id": "project_id",
                        "json_response": {
                            "JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}
                        },
                        "label_asset_external_id": "asset6",
                    },
                    "expected_mutation_call_count": 2,
                },
            ),
            (
                "AAU, when I import predictions from a CSV, I see a success",
                {
                    "files": [],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                        "from-csv": "labels_to_import.csv",
                    },
                    "flags": ["prediction"],
                    "mutation_to_call": "create_predictions",
                    "expected_mutation_payload": {
                        "project_id": "project_id",
                        "json_response_array": [
                            {
                                "JOB_0": {
                                    "categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]
                                }
                            }
                        ]
                        * 2,
                        "external_id_array": ["asset1", "asset6"],
                        "model_name_array": ["model_name"] * 2,
                    },
                },
            ),
        ],
    )
    def test_import_labels(self, mocker, name, test_case):
        """
        Legacy tests that call the Kili import. To split into a CLI tests and
        a service test.
        """
        _, _ = mocker, name
        runner = CliRunner()
        with runner.isolated_filesystem():

            os.mkdir("test_tree")
            # pylint: disable=unspecified-encoding
            with open("test_tree/asset1.json", "w") as outfile:
                json.dump(mock_label, outfile)
            with open("test_tree/asset2.json", "w") as outfile:
                json.dump(mock_label, outfile)
            os.mkdir("test_tree/leaf_1")
            with open("test_tree/leaf_1/asset3.json", "w") as outfile:
                json.dump(mock_label, outfile)
            with open("test_tree/leaf_1/asset4.json", "w") as outfile:
                json.dump(mock_label, outfile)
            os.mkdir("test_tree/leaf_2")
            with open("test_tree/leaf_2/asset5.json", "w") as outfile:
                json.dump(mock_label, outfile)
            with open("test_tree/leaf_2/asset6.json", "w") as outfile:
                json.dump(mock_label, outfile)
            with open("labels_to_import.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(["label_asset_external_id", "path"])
                writer.writerow(["asset1", "test_tree/asset1.json"])
                writer.writerow(["asset6", "test_tree/leaf_2/asset6.json"])

            kili_client.append_to_labels = append_to_labels_mock = MagicMock()
            arguments = test_case["files"]
            for k, v in test_case["options"].items():
                arguments.append("--" + k)
                arguments.append(v)
            if test_case.get("flags"):
                arguments.extend(["--" + flag for flag in test_case["flags"]])
            result = runner.invoke(import_labels, arguments)
            debug_subprocess_pytest(result)
            if test_case["mutation_to_call"] == "append_to_labels":
                assert append_to_labels_mock.call_count == test_case["expected_mutation_call_count"]
                append_to_labels_mock.assert_any_call(**test_case["expected_mutation_payload"])
            else:
                create_predictions_mock.assert_called_with(**test_case["expected_mutation_payload"])

    @pytest.mark.parametrize(
        "name,test_case",
        [
            (
                "AAU, when I import Yolo v4 predictions from a CSV, I see a success",
                {
                    "files": [],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                        "from-csv": "labels_to_import.csv",
                        "metadata-file": "classes.txt",
                        "input-format": "yolo_v4",
                        "target-job": "job_0",
                    },
                    "flags": ["prediction"],
                    "expected_service_call": (
                        ANY,
                        "labels_to_import.csv",
                        [],
                        "classes.txt",
                        "project_id",
                        "yolo_v4",
                        "job_0",
                        True,
                        "WARNING",
                        "model_name",
                        True,
                    ),
                },
            ),
            (
                "AAU, when I import Yolo v5 predictions from a CSV, I see a success",
                {
                    "files": [],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                        "from-csv": "labels_to_import.csv",
                        "metadata-file": "classes.yaml",
                        "input-format": "yolo_v5",
                        "target-job": "job_0",
                    },
                    "flags": ["prediction"],
                    "expected_service_call": (
                        ANY,
                        "labels_to_import.csv",
                        [],
                        "classes.yaml",
                        "project_id",
                        "yolo_v5",
                        "job_0",
                        True,
                        "WARNING",
                        "model_name",
                        True,
                    ),
                },
            ),
        ],
    )
    def test_import_labels_yolo(self, mocker, name, test_case):
        _ = name
        runner = CliRunner()
        with runner.isolated_filesystem():

            with patch(
                "kili.services.label_import.import_labels_from_files"
            ) as mocked_import_labels_service:
                arguments = test_case["files"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
                result = runner.invoke(import_labels, arguments)
                debug_subprocess_pytest(result)
                mocked_import_labels_service.assert_called_with(*test_case["expected_service_call"])
