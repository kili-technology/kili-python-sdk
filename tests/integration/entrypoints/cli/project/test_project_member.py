"""Tests the Kili CLI project member commands."""

import csv
from typing import Dict, List

import pytest
import pytest_mock
from click.testing import CliRunner

from kili.core.graphql.operations.project_user.queries import ProjectUserQuery
from kili.entrypoints.cli.project.member.add import add_member
from kili.entrypoints.cli.project.member.list_ import list_members
from kili.entrypoints.cli.project.member.remove import remove_member
from kili.entrypoints.cli.project.member.update import update_member
from tests.integration.entrypoints.cli.helpers import debug_subprocess_pytest


def mocked__project_user_query(**kwargs):
    if kwargs["where"].project_id == "project_id_source":
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
    elif kwargs["where"].project_id == "new_project":
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


def test_list_members(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(ProjectUserQuery, "__call__", side_effect=mocked__project_user_query)

    runner = CliRunner()
    result = runner.invoke(list_members, ["project_id"])
    debug_subprocess_pytest(result)
    assert result.output.count("Jane Doe") == 1
    assert result.output.count("@test.com") == 2


@pytest.mark.parametrize(
    ("case_name", "inputs", "options", "expected_mutation_payload"),
    [
        (
            "AAU, when I add one user with email adress, I see a success",
            ["bob@test.com", "alice@test.com"],
            {"project-id": "new_project"},
            {"project_id": "new_project", "user_email": "alice@test.com", "role": "LABELER"},
        ),
        (
            "AAU, when I add user from another project, I see a success",
            [],
            {"project-id": "new_project", "from-project": "project_id_"},
            {"project_id": "new_project", "user_email": "jane.doe@test.com", "role": "LABELER"},
        ),
        (
            "AAU, when I add one user with csv file, I see a success",
            [],
            {"project-id": "new_project", "from-csv": "user_list.csv", "role": "REVIEWER"},
            {"project_id": "new_project", "user_email": "bob@test.com", "role": "REVIEWER"},
        ),
    ],
)
def test_add_member(
    case_name: str,
    inputs: List[str],
    options: Dict[str, str],
    expected_mutation_payload: Dict[str, str],
    mocker: pytest_mock.MockerFixture,
):
    append_to_roles_mock = mocker.patch(
        "kili.entrypoints.mutations.project.MutationsProject.append_to_roles"
    )
    mocker.patch.object(ProjectUserQuery, "__call__", side_effect=mocked__project_user_query)

    runner = CliRunner()
    with runner.isolated_filesystem():
        # pylint: disable=unspecified-encoding
        with open("user_list.csv", "w", newline="") as f:
            # newline="" to disable universal newlines translation (bug fix for windows)
            writer = csv.writer(f)
            writer.writerow(["email"])
            writer.writerow(["alice@test.com"])
            writer.writerow(["bob@test.com"])

        arguments = inputs
        for k, v in options.items():
            arguments.append("--" + k)
            arguments.append(v)
        result = runner.invoke(add_member, arguments)
        debug_subprocess_pytest(result)
        append_to_roles_mock.assert_called_with(**expected_mutation_payload)


@pytest.mark.parametrize(
    ("case_name", "inputs", "options", "expected_mutation_payload"),
    [
        (
            "AAU, when I update user's role with email adress, I see a success",
            ["john.doe@test.com", "jane.doe@test.com"],
            {"project-id": "project_id", "role": "REVIEWER"},
            {
                "role_id": "role_id_jane",
                "project_id": "project_id",
                "user_id": "user_id_jane",
                "role": "REVIEWER",
            },
        ),
        (
            "AAU, when I update user's role from another project, I see a success",
            [],
            {"project-id": "project_id", "from-project": "project_id_source"},
            {
                "role_id": "role_id_jane",
                "project_id": "project_id",
                "user_id": "user_id_jane",
                "role": "REVIEWER",
            },
        ),
        (
            "AAU, when I update user's role with csv file, I see a success",
            [],
            {"project-id": "project_id", "from-csv": "user_list.csv", "role": "REVIEWER"},
            {
                "role_id": "role_id_jane",
                "project_id": "project_id",
                "user_id": "user_id_jane",
                "role": "REVIEWER",
            },
        ),
    ],
)
def test_update_member(
    case_name: str,
    inputs: List[str],
    options: Dict[str, str],
    expected_mutation_payload: Dict[str, str],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.dict("os.environ", {"KILI_API_KEY": "fake_key", "KILI_SDK_SKIP_CHECKS": "True"})
    mocker.patch.object(ProjectUserQuery, "__call__", side_effect=mocked__project_user_query)
    update_properties_in_role_mock = mocker.patch(
        "kili.entrypoints.mutations.project.MutationsProject.update_properties_in_role"
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        # pylint: disable=unspecified-encoding
        # newline="" to disable universal newlines translation (bug fix for windows)
        with open("user_list.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["email"])
            writer.writerow(["john.doe@test.com"])
            writer.writerow(["jane.doe@test.com"])

        arguments = inputs
        for k, v in options.items():
            arguments.append("--" + k)
            arguments.append(v)
        result = runner.invoke(update_member, arguments)
        debug_subprocess_pytest(result)
        update_properties_in_role_mock.assert_called_with(**expected_mutation_payload)


@pytest.mark.parametrize(
    ("case_name", "inputs", "options", "flags", "expected_mutation_payload"),
    [
        (
            "AAU, when I remove users with email adress, I see a success",
            ["john.doe@test.com", "jane.doe@test.com"],
            {"project-id": "project_id"},
            None,
            {"role_id": "role_id_jane"},
        ),
        (
            "AAU, when I remove all users, I see a success",
            [],
            {"project-id": "project_id"},
            ["all"],
            {"role_id": "role_id_jane"},
        ),
        (
            "AAU, when I remove users with a  csv file, I see a success",
            [],
            {"project-id": "project_id", "from-csv": "user_list.csv"},
            None,
            {"role_id": "role_id_jane"},
        ),
    ],
)
def test_remove_member(
    case_name: str,
    inputs: List[str],
    options: Dict[str, str],
    flags: List[str],
    expected_mutation_payload: Dict[str, str],
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.dict("os.environ", {"KILI_API_KEY": "fake_key", "KILI_SDK_SKIP_CHECKS": "True"})
    mocker.patch.object(ProjectUserQuery, "__call__", side_effect=mocked__project_user_query)
    delete_from_roles_mock = mocker.patch(
        "kili.entrypoints.mutations.project.MutationsProject.delete_from_roles"
    )

    runner = CliRunner()
    with runner.isolated_filesystem():
        # pylint: disable=unspecified-encoding
        # newline="" to disable universal newlines translation (bug fix for windows)
        with open("user_list.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["email"])
            writer.writerow(["john.doe@test.com"])
            writer.writerow(["jane.doe@test.com"])

        arguments = inputs
        for k, v in options.items():
            arguments.append("--" + k)
            arguments.append(v)
        if flags:
            arguments.extend(["--" + flag for flag in flags])
        result = runner.invoke(remove_member, arguments)
        debug_subprocess_pytest(result)
        delete_from_roles_mock.assert_called_with(**expected_mutation_payload)
