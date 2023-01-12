import json
import os
from unittest.mock import ANY, MagicMock, patch

import pytest
from click.testing import CliRunner

from kili.cli.project.label import import_labels
from kili.graphql.operations.project.queries import ProjectQuery

from ...utils import debug_subprocess_pytest
from .mocks.projects import mocked__ProjectsQuery

kili_client = MagicMock()
kili_client.create_predictions = create_predictions_mock = MagicMock()

mock_label = {"JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}}


@patch("kili.client.Kili.__new__", return_value=kili_client)
@patch.object(ProjectQuery, "__call__", side_effect=mocked__ProjectsQuery)
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
                    "expected_service_call": (
                        ANY,
                        ["test_tree/leaf_1/", "test_tree/asset1.json", "test_tree/leaf_2/**.json"],
                        None,
                        "project_id",
                        "kili",
                        None,
                        True,
                        "WARNING",
                        None,
                        False,
                    ),
                },
            ),
            (
                "AAU, when I import predictions, I see a success",
                {
                    "files": [
                        "test_tree/asset1.json",
                        "test_tree/leaf_2/asset6.json",
                    ],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                    },
                    "flags": ["prediction"],
                    "expected_service_call": (
                        ANY,
                        ["test_tree/asset1.json", "test_tree/leaf_2/asset6.json"],
                        None,
                        "project_id",
                        "kili",
                        None,
                        True,
                        "WARNING",
                        "model_name",
                        True,
                    ),
                },
            ),
        ],
    )
    def test_import_labels(
        self,
        mocker_project,
        mocker_kili,
        name,
        test_case,
    ):
        """
        Test that the CLI properly calls the label_import service
        """
        print()
        _, _, _ = mocker_project, mocker_kili, name
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
                arguments = test_case["files"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
        with patch("kili.services.import_labels_from_files") as mocked_import_labels_service:
            result = runner.invoke(import_labels, arguments)
            debug_subprocess_pytest(result)
            mocked_import_labels_service.assert_called_with(*test_case["expected_service_call"])

    @pytest.mark.parametrize(
        "name,test_case",
        [
            (
                "AAU, when I import Yolo v4 predictions, I see a success",
                {
                    "files": [
                        "test_tree/leaf_1/",
                        "test_tree/asset1.json",
                        "test_tree/leaf_2/**.json",
                    ],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                        "metadata-file": "classes.txt",
                        "input-format": "yolo_v4",
                        "target-job": "job_0",
                    },
                    "flags": ["prediction"],
                    "expected_service_call": (
                        ANY,
                        ["test_tree/leaf_1/", "test_tree/asset1.json", "test_tree/leaf_2/**.json"],
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
                "AAU, when I import Yolo v5 predictions, I see a success",
                {
                    "files": [
                        "test_tree/leaf_1/",
                        "test_tree/asset1.json",
                        "test_tree/leaf_2/**.json",
                    ],
                    "options": {
                        "project-id": "project_id",
                        "model-name": "model_name",
                        "metadata-file": "classes.yaml",
                        "input-format": "yolo_v5",
                        "target-job": "job_0",
                    },
                    "flags": ["prediction"],
                    "expected_service_call": (
                        ANY,
                        ["test_tree/leaf_1/", "test_tree/asset1.json", "test_tree/leaf_2/**.json"],
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
    def test_import_labels_yolo(self, _mocker_project, _mocker_kili, name, test_case):
        _ = name
        runner = CliRunner()
        with runner.isolated_filesystem():
            with patch("kili.services.import_labels_from_files") as mocked_import_labels_service:
                arguments = test_case["files"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
                result = runner.invoke(import_labels, arguments)
                debug_subprocess_pytest(result)
                mocked_import_labels_service.assert_called_with(*test_case["expected_service_call"])
