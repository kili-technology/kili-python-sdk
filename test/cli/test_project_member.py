"""Tests the Kili CLI project member commands"""

import csv
import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from kili.cli.project.member.add import add_member
from kili.cli.project.member.list_ import list_members
from kili.cli.project.member.remove import remove_member
from kili.cli.project.member.update import update_member

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


kili_client = MagicMock()
kili_client.auth.client.endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql"
kili_client.project_users = project_users_mock = MagicMock(side_effect=mocked__project_users)
kili_client.append_to_roles = append_to_roles_mock = MagicMock()
kili_client.update_properties_in_role = update_properties_in_role_mock = MagicMock()
kili_client.delete_from_roles = delete_from_roles_mock = MagicMock()

kili = MagicMock()
kili.Kili = MagicMock(return_value=kili_client)


@patch("kili.client.Kili.__new__", return_value=kili_client)
class TestCLIProjectMember:
    """
    test the CLI functions of the project member commands
    """

    def test_list_members(self, mocker):
        runner = CliRunner()
        result = runner.invoke(list_members, ["project_id"])
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
