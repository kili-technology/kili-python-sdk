"""Tests the Kili CLI"""

import csv
from unittest.mock import MagicMock, patch
import os

from click.testing import CliRunner
from kili.cli.project.create import create_project
from kili.cli.project.describe import describe_project
from kili.cli.project.import_ import import_assets
from kili.cli.project.label import import_labels
from kili.cli.project.list_ import list_projects
from kili.cli.project.member.list_ import list_members
from kili.cli.project.member.add import add_member
from kili.cli.project.member.update import update_member
from kili.cli.project.member.remove import remove_member

from ..utils import debug_subprocess_pytest


def mocked__project_users(project_id=None, **_):
    if project_id == "project_id_source":
        return [
            {
                "activated": True,
                "id": "role_id_src_alice",
                "role": "ADMIN",
                "user": {
                    "email": "alice@test.com",
                    "firstname": "alice",
                    "id": "user_id_alice",
                    "lastname": "alice",
                    "organization": {"name": "test"},
                },
            },
            {
                "activated": True,
                "id": "role_id_src_bob",
                "role": "LABELER",
                "user": {
                    "email": "bob@test.com",
                    "firstname": "bob",
                    "id": "user_id_bob",
                    "lastname": "bob",
                    "organization": {"name": "test"},
                },
            },
            {
                "activated": True,
                "id": "role_id_src_john",
                "role": "REVIEWER",
                "user": {
                    "email": "john.doe@test.com",
                    "firstname": "john",
                    "id": "user_id_john",
                    "lastname": "doe",
                    "organization": {"name": "test"},
                },
            },
            {
                "activated": True,
                "id": "role_id_src_jane",
                "role": "REVIEWER",
                "user": {
                    "email": "jane.doe@test.com",
                    "firstname": "jane",
                    "id": "user_id_jane",
                    "lastname": "doe",
                    "organization": {"name": "test"},
                },
            },
        ]
    elif project_id == "new_project":
        return []
    else:
        return [
            {
                "activated": True,
                "id": "role_id_john",
                "role": "ADMIN",
                "user": {
                    "email": "john.doe@test.com",
                    "firstname": "john",
                    "id": "user_id_john",
                    "lastname": "doe",
                    "organization": {"name": "test"},
                },
            },
            {
                "activated": True,
                "id": "role_id_jane",
                "role": "LABELER",
                "user": {
                    "email": "jane.doe@test.com",
                    "firstname": "jane",
                    "id": "user_id_jane",
                    "lastname": "doe",
                    "organization": {"name": "test"},
                },
            },
        ]


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


kili_client = MagicMock()
kili_client.auth.client.endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql"
kili_client.projects = project_mock = MagicMock(side_effect=mocked__projects)
kili_client.append_to_labels = append_to_labels_mock = MagicMock()
kili_client.create_predictions = create_predictions_mock = MagicMock()
kili_client.count_projects = count_projects_mock = MagicMock(return_value=1)
kili_client.append_many_to_dataset = append_many_to_dataset_mock = MagicMock()
kili_client.create_project = create_project_mock = MagicMock()
kili_client.project_users = project_users_mock = MagicMock(side_effect=mocked__project_users)
kili_client.append_to_roles = append_to_roles_mock = MagicMock()
kili_client.update_properties_in_role = update_properties_in_role_mock = MagicMock()
kili_client.delete_from_roles = delete_from_roles_mock = MagicMock()

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
                "case_name": "AAU, when I import default labels from a CSV, I see a success",
                "options": {
                    "project-id": "project_id",
                    "from-csv": "test/fixtures/labels_to_import.csv",
                },
                "flags": [],
                "mutation_to_call": "append_to_labels",
                "expected_mutation_payload": {
                    "project_id": "project_id",
                    "json_response": {
                        "JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}
                    },
                    "label_asset_external_id": "poules.png",
                },
            },
            {
                "case_name": "AAU, when I import predictions from a CSV, I see a sucess",
                "options": {
                    "project-id": "project_id",
                    "model-name": "model_name",
                    "from-csv": "test/fixtures/labels_to_import.csv",
                },
                "flags": ["prediction"],
                "mutation_to_call": "create_predictions",
                "expected_mutation_payload": {
                    "project_id": "project_id",
                    "json_response_array": [
                        {"JOB_0": {"categories": [{"name": "YES_IT_IS_SPAM", "confidence": 100}]}}
                    ]
                    * 2,
                    "external_id_array": ["poules.png", "test.jpg"],
                    "model_name_array": ["model_name"] * 2,
                },
            },
        ]
        runner = CliRunner()
        for test_case in TEST_CASES:
            arguments = []
            for k, v in test_case["options"].items():
                arguments.append("--" + k)
                arguments.append(v)
            if test_case.get("flags"):
                arguments.extend(["--" + flag for flag in test_case["flags"]])
            result = runner.invoke(import_labels, arguments)
            debug_subprocess_pytest(result)
            if test_case["mutation_to_call"] == "append_to_labels":
                append_to_labels_mock.assert_any_call(**test_case["expected_mutation_payload"])
            else:
                create_predictions_mock.assert_called_with(**test_case["expected_mutation_payload"])

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
                    "external_id_array": ["image1.png", "image3.png"],
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
                    "external_id_array": ["image2.jpg", "image4.jpg"],
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
                    "external_id_array": ["texte2.txt", "texte1.txt"],
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
                    "external_id_array": ["video1.mp4", "video2.mp4"],
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
                    "external_id_array": ["video1.mp4", "video2.mp4"],
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
                    "external_id_array": ["image3s.png", "test.svg"],
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
                writer.writerow(["image3s.png", "test_tree/leaf/image3.png"])
                writer.writerow(
                    [
                        "test.svg",
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

    def test_list_members(self, mocker):
        runner = CliRunner()
        result = runner.invoke(list_members, ["--project-id", "project_id"])
        debug_subprocess_pytest(result)
        assert (result.output.count("Jane Doe") == 1) and (result.output.count("@test.com") == 2)

    def test_add_member(self, mocker):
        TEST_CASES = [
            {
                "case_name": "AAU, when I add one user with email adress, I see a success",
                "inputs": ["bob@test.com", "alice@test.com"],
                "options": {
                    "project-id": "new_project",
                },
                "expected_mutation_payload": {
                    "project_id": "new_project",
                    "user_email": "alice@test.com",
                    "role": "LABELER",
                },
            },
            {
                "case_name": "AAU, when I add user from another project, I see a success",
                "inputs": [],
                "options": {"project-id": "new_project", "from-project": "project_id_"},
                "expected_mutation_payload": {
                    "project_id": "new_project",
                    "user_email": "jane.doe@test.com",
                    "role": "LABELER",
                },
            },
            {
                "case_name": "AAU, when I add one user with csv file, I see a success",
                "inputs": [],
                "options": {
                    "project-id": "new_project",
                    "from-csv": "user_list.csv",
                    "role": "REVIEWER",
                },
                "expected_mutation_payload": {
                    "project_id": "new_project",
                    "user_email": "bob@test.com",
                    "role": "REVIEWER",
                },
            },
        ]
        runner = CliRunner()
        with runner.isolated_filesystem():
            # pylint: disable=unspecified-encodind
            with open("user_list.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(["email"])
                writer.writerow(["alice@test.com"])
                writer.writerow(["bob@test.com"])

            for i, test_case in enumerate(TEST_CASES):
                print(test_case["case_name"])
                arguments = test_case["inputs"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                result = runner.invoke(add_member, arguments)
                debug_subprocess_pytest(result)
                assert append_to_roles_mock.call_count == 2 * (i + 1)
                append_to_roles_mock.assert_called_with(**test_case["expected_mutation_payload"])

    def test_update_member(self, mocker):
        TEST_CASES = [
            {
                "case_name": "AAU, when I update user's role with email adress, I see a success",
                "inputs": ["john.doe@test.com", "jane.doe@test.com"],
                "options": {"project-id": "project_id", "role": "REVIEWER"},
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                    "project_id": "project_id",
                    "user_id": "user_id_jane",
                    "role": "REVIEWER",
                },
            },
            {
                "case_name": "AAU, when I update user's role from another project, I see a success",
                "inputs": [],
                "options": {
                    "project-id": "project_id",
                    "from-project": "project_id_source",
                },
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                    "project_id": "project_id",
                    "user_id": "user_id_jane",
                    "role": "REVIEWER",
                },
            },
            {
                "case_name": "AAU, when I update user's role with csv file, I see a success",
                "inputs": [],
                "options": {
                    "project-id": "project_id",
                    "from-csv": "user_list.csv",
                    "role": "REVIEWER",
                },
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                    "project_id": "project_id",
                    "user_id": "user_id_jane",
                    "role": "REVIEWER",
                },
            },
        ]
        runner = CliRunner()
        with runner.isolated_filesystem():
            # pylint: disable=unspecified-encodind
            with open("user_list.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(["email"])
                writer.writerow(["john.doe@test.com"])
                writer.writerow(["jane.doe@test.com"])

            for i, test_case in enumerate(TEST_CASES):
                print(test_case["case_name"])
                arguments = test_case["inputs"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                result = runner.invoke(update_member, arguments)
                debug_subprocess_pytest(result)
                assert update_properties_in_role_mock.call_count == 2 * (i + 1)
                update_properties_in_role_mock.assert_called_with(
                    **test_case["expected_mutation_payload"]
                )

    def test_remove_member(self, mocker):
        TEST_CASES = [
            {
                "case_name": "AAU, when I remove users with email adress, I see a success",
                "inputs": ["john.doe@test.com", "jane.doe@test.com"],
                "options": {
                    "project-id": "project_id",
                },
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                },
            },
            {
                "case_name": "AAU, when I remove all users, I see a success",
                "inputs": [],
                "options": {
                    "project-id": "project_id",
                },
                "flags": ["all"],
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                },
            },
            {
                "case_name": "AAU, when I remove users with a  csv file, I see a success",
                "inputs": [],
                "options": {
                    "project-id": "project_id",
                    "from-csv": "user_list.csv",
                },
                "expected_mutation_payload": {
                    "role_id": "role_id_jane",
                },
            },
        ]
        runner = CliRunner()
        with runner.isolated_filesystem():
            # pylint: disable=unspecified-encodind
            with open("user_list.csv", "w") as f:
                writer = csv.writer(f)
                writer.writerow(["email"])
                writer.writerow(["john.doe@test.com"])
                writer.writerow(["jane.doe@test.com"])

            for i, test_case in enumerate(TEST_CASES):
                print(test_case["case_name"])
                arguments = test_case["inputs"]
                for k, v in test_case["options"].items():
                    arguments.append("--" + k)
                    arguments.append(v)
                if test_case.get("flags"):
                    arguments.extend(["--" + flag for flag in test_case["flags"]])
                result = runner.invoke(remove_member, arguments)
                debug_subprocess_pytest(result)
                assert delete_from_roles_mock.call_count == 2 * (i + 1)
                delete_from_roles_mock.assert_called_with(**test_case["expected_mutation_payload"])
