"""Tests the Kili CLI"""

import csv
import json
import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from kili.cli.project.create import create_project
from kili.cli.project.describe import describe_project
from kili.cli.project.import_ import import_assets
from kili.cli.project.label import import_labels
from kili.cli.project.list_ import list_projects

from ..utils import debug_subprocess_pytest

mock_label = {"JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}}


def mocked__projects(project_id=None, **_):
    if project_id == "text_project":
        return [{"id": "text_project", "inputType": "TEXT"}]
    if project_id == "image_project":
        return [{"id": "image_project", "inputType": "IMAGE"}]
    if project_id == "frame_project":
        return [{"id": "frame_project", "inputType": "VIDEO"}]
    if project_id == None:
        return [
            {
                "id": "text_project",
                "title": "text_project",
                "description": " a project with text",
                "numberOfAssets": 10,
                "numberOfRemainingAssets": 10,
            },
            {
                "id": "image_project",
                "title": "image_project",
                "description": " a project with image",
                "numberOfAssets": 0,
                "numberOfRemainingAssets": 0,
            },
            {
                "id": "frame_project",
                "title": "frame_project",
                "description": " a project with frame",
                "numberOfAssets": 10,
                "numberOfRemainingAssets": 0,
            },
        ]
    if project_id == "project_id":
        return [
            {
                "title": "project title",
                "id": "project_id",
                "description": "description test",
                "numberOfAssets": 49,
                "numberOfRemainingAssets": 29,
                "numberOfReviewedAssets": 0,
                "numberOfSkippedAssets": 0,
                "numberOfOpenIssues": 3,
                "numberOfSolvedIssues": 2,
                "numberOfOpenQuestions": 0,
                "numberOfSolvedQuestions": 2,
                "honeypotMark": None,
                "consensusMark": None,
            }
        ]


def mocked__project_assets(**_):
    return [
        {"externalId": "asset1"},
        {"externalId": "asset2"},
        {"externalId": "asset3"},
        {"externalId": "asset4"},
        {"externalId": "asset5"},
        {"externalId": "asset6"},
    ]


kili_client = MagicMock()
kili_client.auth.client.endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql"
kili_client.projects = project_mock = MagicMock(side_effect=mocked__projects)
kili_client.append_to_labels = append_to_labels_mock = MagicMock()
kili_client.create_predictions = create_predictions_mock = MagicMock()
kili_client.count_projects = count_projects_mock = MagicMock(return_value=1)
kili_client.append_many_to_dataset = append_many_to_dataset_mock = MagicMock()
kili_client.create_project = create_project_mock = MagicMock()
kili_client.assets = assets_mock = MagicMock(side_effect=mocked__project_assets)

kili = MagicMock()
kili.Kili = MagicMock(return_value=kili_client)


@patch("kili.client.Kili.__new__", return_value=kili_client)
class TestCLIProject:
    """
    test the CLI functions of the project command
    """

    def test_list(self, mocker):
        runner = CliRunner()
        result = runner.invoke(list_projects)
        assert (
            (result.exit_code == 0)
            and (result.output.count("100.0%") == 1)
            and (result.output.count("0.0%") == 2)
            and (result.output.count("nan") == 1)
        )

    def test_create_project(self, mocker):
        runner = CliRunner()
        runner.invoke(
            create_project,
            [
                "--interface",
                "test/fixtures/image_interface.json",
                "--title",
                "Test project",
                "--description",
                "description",
                "--input-type",
                "IMAGE",
            ],
        )

    def test_describe_project(self, mocker):
        runner = CliRunner()
        result = runner.invoke(describe_project, ["project_id"])
        debug_subprocess_pytest(result)
        assert (
            (result.output.count("40.8%") == 1)
            and (result.output.count("N/A") == 2)
            and (result.output.count("49") == 1)
            and (result.output.count("project title") == 1)
        )

    def test_import_labels(self, mocker):
        TEST_CASES = [
            {
                "case_name": "AAU, when I import a list of label's file to project, I see a success",
                "files": ["test_tree/leaf_1/", "test_tree/asset1.json", "test_tree/leaf_2/**.json"],
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
            },
            {
                "case_name": "AAU, when I import default labels from a CSV, I see a success",
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
            },
            {
                "case_name": "AAU, when I import predictions from a CSV, I see a sucess",
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
                        {"JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}}
                    ]
                    * 2,
                    "external_id_array": ["asset1", "asset6"],
                    "model_name_array": ["model_name"] * 2,
                },
            },
        ]
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
                writer.writerow(["external_id", "json_response_path"])
                writer.writerow(["asset1", "test_tree/asset1.json"])
                writer.writerow(["asset6", "test_tree/leaf_2/asset6.json"])

            for i, test_case in enumerate(TEST_CASES):
                arguments = test_case["files"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
                print(arguments)
                result = runner.invoke(import_labels, arguments)
                debug_subprocess_pytest(result)
                if test_case["mutation_to_call"] == "append_to_labels":
                    assert append_to_labels_mock.call_count == 5 + 2 * i
                    append_to_labels_mock.assert_any_call(**test_case["expected_mutation_payload"])
                else:
                    create_predictions_mock.assert_called_with(
                        **test_case["expected_mutation_payload"]
                    )

    def test_import(self, mocker):
        TEST_CASES = [
            {
                "case_name": "AAU, when I import a list of file to an image project, I see a success",
                "files": ["test_tree/image1.png", "test_tree/leaf/image3.png"],
                "options": {
                    "project-id": "image_project",
                },
                "expected_mutation_payload": {
                    "project_id": "image_project",
                    "content_array": [
                        "test_tree/image1.png",
                        "test_tree/leaf/image3.png",
                    ],
                    "external_id_array": ["image1", "image3"],
                    "json_metadata_array": None,
                },
            },
            {
                "case_name": "AAU, when I import files with stars, I see a success",
                "files": ["test_tree/**.jpg", "test_tree/leaf/**.jpg"],
                "options": {
                    "project-id": "image_project",
                },
                "expected_mutation_payload": {
                    "project_id": "image_project",
                    "content_array": [
                        "test_tree/image2.jpg",
                        "test_tree/leaf/image4.jpg",
                    ],
                    "external_id_array": ["image2", "image4"],
                    "json_metadata_array": None,
                },
            },
            {
                "case_name": "AAU, when I import a files to a text project, I see a success",
                "files": ["test_tree/", "test_tree/leaf"],
                "options": {"project-id": "text_project"},
                "expected_mutation_payload": {
                    "project_id": "text_project",
                    "content_array": [
                        "test_tree/leaf/texte2.txt",
                        "test_tree/texte1.txt",
                    ],
                    "external_id_array": ["texte2", "texte1"],
                    "json_metadata_array": None,
                },
            },
            {
                "case_name": "AAU, when I import videos to a video project, as native by changing the fps, I see a success",
                "files": ["test_tree/"],
                "options": {
                    "project-id": "frame_project",
                    "fps": "10",
                },
                "expected_mutation_payload": {
                    "project_id": "frame_project",
                    "content_array": ["test_tree/video1.mp4", "test_tree/video2.mp4"],
                    "external_id_array": ["video1", "video2"],
                    "json_metadata_array": [
                        {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        }
                    ]
                    * 2,
                },
            },
            {
                "case_name": "AAU, when I import videos to a video project, as frames with the native frame rate, I see a success",
                "files": ["test_tree/"],
                "options": {
                    "project-id": "frame_project",
                },
                "flags": ["frames"],
                "expected_mutation_payload": {
                    "project_id": "frame_project",
                    "content_array": ["test_tree/video1.mp4", "test_tree/video2.mp4"],
                    "external_id_array": ["video1", "video2"],
                    "json_metadata_array": [
                        {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        }
                    ]
                    * 2,
                },
            },
            {
                "case_name": "AAU, when I import assets from a csv file, I see a success",
                "files": [],
                "options": {
                    "project-id": "image_project",
                    "from-csv": "assets_to_import.csv",
                },
                "expected_mutation_payload": {
                    "project_id": "image_project",
                    "content_array": (
                        [
                            "test_tree/leaf/image3.png",
                            "https://files.readme.io/cac9114-Kili_Wordmark_SoftWhite_RGB.svg",
                        ]
                    ),
                    "external_id_array": ["image3", "test"],
                    "json_metadata_array": None,
                },
            },
        ]
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir("test_tree")
            # pylint: disable=unspecified-encoding
            open("test_tree/image1.png", "w")
            open("test_tree/image2.jpg", "w")
            open("test_tree/texte1.txt", "w")
            open("test_tree/video1.mp4", "w")
            open("test_tree/video2.mp4", "w")
            os.mkdir("test_tree/leaf")
            open("test_tree/leaf/image3.png", "w")
            open("test_tree/leaf/image4.jpg", "w")
            open("test_tree/leaf/texte2.txt", "w")
            with open("assets_to_import.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(["external_id", "content"])
                writer.writerow(["image3", "test_tree/leaf/image3.png"])
                writer.writerow(
                    [
                        "test",
                        "https://files.readme.io/cac9114-Kili_Wordmark_SoftWhite_RGB.svg",
                    ]
                )

            for test_case in TEST_CASES:
                arguments = test_case["files"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
                print(arguments)
                result = runner.invoke(import_assets, arguments)
                debug_subprocess_pytest(result)
                append_many_to_dataset_mock.assert_called_with(
                    **test_case["expected_mutation_payload"]
                )
