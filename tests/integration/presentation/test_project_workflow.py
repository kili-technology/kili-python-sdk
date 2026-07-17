import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project_workflow.operations import (
    get_update_project_workflow_mutation,
)
from kili.presentation.client.project_workflow import ProjectWorkflowClientMethods
from kili.use_cases.project_workflow import ProjectWorkflowUseCases

_UPDATE_FRAGMENT = " enforceStepSeparation steps{id}"


def _client(mocker: pytest_mock.MockerFixture) -> ProjectWorkflowClientMethods:
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    return kili


def _member(email: str, user_id: str, role: str) -> dict:
    return {"role": role, "user": {"id": user_id, "email": email}, "activated": True}


def _project_users_results(members: list[dict]) -> list[dict]:
    return [{"data": len(members)}, {"data": members}]


def _context_result(workflow_version: str, steps: list[dict], step_groups: list[dict]) -> dict:
    return {
        "data": [{"workflowVersion": workflow_version, "steps": steps, "stepGroups": step_groups}]
    }


_MUTATION_RESULT = {"data": {"id": "proj"}}


def _last_update_variables(kili: ProjectWorkflowClientMethods) -> dict:
    last_call = kili.kili_api_gateway.graphql_client.execute.call_args_list[-1]
    assert last_call.args[0] == get_update_project_workflow_mutation(_UPDATE_FRAGMENT)
    return last_call.args[1]["input"]


def test_when_updating_project_workflow_then_it_returns_updated_project_workflow(
    mocker: pytest_mock.MockerFixture,
):
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    kili.update_project_workflow(project_id, enforce_step_separation=False)

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_update_project_workflow_mutation(" enforceStepSeparation steps{id}"),
        {
            "input": {
                "projectId": "fake_proj_id",
                "enforceStepSeparation": False,
                "steps": {
                    "creates": [],
                    "deletes": [],
                    "updates": [],
                },
            },
        },
    )


def test_when_getting_steps_then_it_returns_steps(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(
        ProjectWorkflowUseCases,
        "get_steps",
        return_value=[{"id": "step_id", "name": "step_name", "type": "step_type"}],
    )
    kili = ProjectWorkflowClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    steps = kili.get_steps(project_id)

    # Then

    assert steps == [{"id": "step_id", "name": "step_name", "type": "step_type"}]


def test_add_reviewers_to_step_on_v2_project(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [
        _member("rev@kili.com", "u-rev", "REVIEWER"),
        _member("lab@kili.com", "u-lab", "LABELER"),
    ]
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": None,
            "assignees": [{"id": "u-existing"}],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V2", steps, []),
        _MUTATION_RESULT,
    ]

    added = kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com"])

    assert added == ["rev@kili.com"]
    variables = _last_update_variables(kili)
    assert variables["projectId"] == "proj"
    assert variables["steps"]["updates"] == [
        {"id": "step-review", "assignees": ["u-existing", "u-rev"]}
    ]


def test_add_reviewers_to_step_skips_labeler_role_emails(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [
        _member("rev@kili.com", "u-rev", "REVIEWER"),
        _member("lab@kili.com", "u-lab", "LABELER"),
    ]
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": None,
            "assignees": [],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V2", steps, []),
        _MUTATION_RESULT,
    ]

    with pytest.warns(UserWarning, match="not found or can not review"):
        added = kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com", "lab@kili.com"])

    assert added == ["rev@kili.com"]


def test_add_reviewers_to_step_on_labeling_step_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("rev@kili.com", "u-rev", "REVIEWER")]
    steps = [
        {
            "id": "step-label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": None,
            "assignees": [],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V2", steps, []),
    ]

    with pytest.raises(ValueError, match="must be a review step"):
        kili.add_reviewers_to_step("proj", "Labeling", ["rev@kili.com"])


def test_remove_reviewers_from_step_on_v2_project(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": None,
            "assignees": [{"id": "u1", "email": "a@kili.com"}, {"id": "u2", "email": "b@kili.com"}],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        _context_result("V2", steps, []),
        _MUTATION_RESULT,
    ]

    removed = kili.remove_reviewers_from_step("proj", "Review", ["a@kili.com"])

    assert removed == ["a@kili.com"]
    variables = _last_update_variables(kili)
    assert variables["steps"]["updates"] == [{"id": "step-review", "assignees": ["u2"]}]


def test_remove_reviewers_leaving_zero_assignees_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": None,
            "assignees": [{"id": "u1", "email": "a@kili.com"}],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [_context_result("V2", steps, [])]

    with pytest.raises(ValueError, match="at least one"):
        kili.remove_reviewers_from_step("proj", "Review", ["a@kili.com"])


def test_add_reviewers_to_step_v3_uses_group_name_to_pick_step(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("rev@kili.com", "u-rev", "REVIEWER")]
    steps = [
        {
            "id": "step-g1-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-1",
            "assignees": [],
        },
        {
            "id": "step-g2-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-2",
            "assignees": [],
        },
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}, {"id": "grp-2", "name": "Group 2"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V3", steps, step_groups),
        _MUTATION_RESULT,
    ]

    added = kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com"], group_name="Group 2")

    assert added == ["rev@kili.com"]
    variables = _last_update_variables(kili)
    assert variables["steps"]["updates"] == [{"id": "step-g2-review", "assignees": ["u-rev"]}]


def test_add_reviewers_to_step_v3_ambiguous_step_name_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("rev@kili.com", "u-rev", "REVIEWER")]
    steps = [
        {
            "id": "step-g1-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-1",
            "assignees": [],
        },
        {
            "id": "step-g2-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-2",
            "assignees": [],
        },
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}, {"id": "grp-2", "name": "Group 2"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V3", steps, step_groups),
    ]

    with pytest.raises(ValueError, match="Multiple steps named 'Review'"):
        kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com"])


def test_add_reviewers_to_step_group_name_not_found_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("rev@kili.com", "u-rev", "REVIEWER")]
    steps = [
        {
            "id": "step-g1-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-1",
            "assignees": [],
        }
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V3", steps, step_groups),
    ]

    with pytest.raises(ValueError, match="Group 'Missing' not found"):
        kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com"], group_name="Missing")


def test_add_reviewers_to_step_group_name_on_v2_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("rev@kili.com", "u-rev", "REVIEWER")]
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": None,
            "assignees": [],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        *_project_users_results(members),
        _context_result("V2", steps, []),
    ]

    with pytest.raises(ValueError, match="group_name is only supported on workflow V3"):
        kili.add_reviewers_to_step("proj", "Review", ["rev@kili.com"], group_name="Group 1")


def test_add_labelers_to_step_v3_default_step(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    members = [_member("lab@kili.com", "u-lab", "LABELER")]
    steps = [
        {
            "id": "step-label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": "grp-1",
            "assignees": [{"id": "u-existing"}],
        }
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        _context_result("V3", steps, step_groups),
        *_project_users_results(members),
        _MUTATION_RESULT,
    ]

    added = kili.add_labelers_to_step("proj", "Labeling", ["lab@kili.com"], group_name="Group 1")

    assert added == ["lab@kili.com"]
    variables = _last_update_variables(kili)
    assert variables["steps"]["updates"] == [
        {"id": "step-label", "assignees": ["u-existing", "u-lab"]}
    ]


def test_add_labelers_to_step_on_review_step_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "grp-1",
            "assignees": [],
        }
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        _context_result("V3", steps, step_groups),
    ]

    with pytest.raises(ValueError, match="must be a labeling step"):
        kili.add_labelers_to_step("proj", "Review", ["lab@kili.com"], group_name="Group 1")


def test_add_labelers_to_step_on_v2_project_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": None,
            "assignees": [],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [_context_result("V2", steps, [])]

    with pytest.raises(ValueError, match="requires a workflow V3 project"):
        kili.add_labelers_to_step("proj", "Labeling", ["lab@kili.com"])


def test_remove_labelers_from_step_v3_default_step(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": "grp-1",
            "assignees": [{"id": "u1", "email": "a@kili.com"}, {"id": "u2", "email": "b@kili.com"}],
        }
    ]
    step_groups = [{"id": "grp-1", "name": "Group 1"}]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [
        _context_result("V3", steps, step_groups),
        _MUTATION_RESULT,
    ]

    removed = kili.remove_labelers_from_step(
        "proj", "Labeling", ["a@kili.com"], group_name="Group 1"
    )

    assert removed == ["a@kili.com"]
    variables = _last_update_variables(kili)
    assert variables["steps"]["updates"] == [{"id": "step-label", "assignees": ["u2"]}]


def test_remove_labelers_from_step_on_v2_project_raises(mocker: pytest_mock.MockerFixture):
    kili = _client(mocker)
    steps = [
        {
            "id": "step-label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": None,
            "assignees": [{"id": "u1", "email": "a@kili.com"}],
        }
    ]
    kili.kili_api_gateway.graphql_client.execute.side_effect = [_context_result("V2", steps, [])]

    with pytest.raises(ValueError, match="requires a workflow V3 project"):
        kili.remove_labelers_from_step("proj", "Labeling", ["a@kili.com"])
