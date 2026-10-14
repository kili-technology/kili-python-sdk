from types import GeneratorType

import pytest

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.types import ProjectDataKiliAPIGatewayInput
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import DeprecatedArgumentError
from kili.use_cases.project.project import ProjectUseCases

interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": [], "name": "Object A"},
                    "OBJECT_B": {"children": [], "name": "Object B"},
                },
                "input": "radio",
            },
            "instruction": "Categories",
            "isChild": False,
            "mlTask": "CLASSIFICATION",
            "models": {},
            "isVisible": True,
            "required": 1,
        }
    }
}


def test_when_create_project_it_works(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.create_project.return_value = "fake_project_id"

    # When
    project_id = ProjectUseCases(kili_api_gateway).create_project(
        input_type="TEXT",
        json_interface={},
        title="test",
        description="description",
        project_id=None,
        compliance_tags=None,
        from_demo_project=None,
    )

    # Then
    assert project_id == "fake_project_id"


def test_when_create_project_without_inputType_or_jsonInterface_it_throw_an_error(
    kili_api_gateway: KiliAPIGateway,
):
    kili_api_gateway.create_project.return_value = "fake_project_id"

    # When
    project_use_cases = ProjectUseCases(kili_api_gateway)

    # Then
    with pytest.raises(
        ValueError,
        match="Arguments `input_type` and `json_interface` must be set if neither `from_demo_project` nor `project_id` is provided",
    ):
        project_use_cases.create_project(
            title="test",
            description="description",
            compliance_tags=None,
            from_demo_project=None,
        )


def test_when_create_project_with_project_id_it_works(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.create_project.return_value = "fake_copied_project_id"
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": interface,
        "instructions": "fake_instructions",
        "inputType": "TEXT",
    }
    kili_api_gateway.list_tags_by_project.return_value = tags
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    project_id = ProjectUseCases(kili_api_gateway).create_project(
        title="test",
        description="description",
        project_id=ProjectId("fake_project_id"),
        compliance_tags=None,
        from_demo_project=None,
    )

    # Then
    assert project_id == "fake_copied_project_id"


def test_when_create_project_with_project_id_it_throw_an_error_if_tags_do_not_belong_to_the_same_organisation(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
    ]
    org_tags = [
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.create_project.return_value = "fake_copied_project_id"
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": interface,
        "instructions": "fake_instructions",
        "inputType": "TEXT",
    }
    kili_api_gateway.list_tags_by_project.return_value = tags
    kili_api_gateway.list_tags_by_org.return_value = org_tags

    # When
    project_use_cases = ProjectUseCases(kili_api_gateway)
    with pytest.raises(
        ValueError,
        match="Tag tag1_id doesn't belong to your organization and was not copied.",
    ):
        project_use_cases.create_project(
            title="test",
            description="description",
            project_id=ProjectId("fake_project_id"),
            compliance_tags=None,
            from_demo_project=None,
        )


def test_when_i_query_projects_i_get_a_generator_of_projects(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_projects = [
        {
            "title": f"fake_proj_title_{i}",
            "id": f"fake_project_id_{i}",
            "jsonInterface": {},
            "inputType": "TEXT",
        }
        for i in range(3)
    ]
    kili_api_gateway.list_projects.return_value = (proj for proj in kili_projects)

    # When
    retrieved_projects = ProjectUseCases(kili_api_gateway).list_projects(
        ProjectFilters(
            id=None,
            archived=None,
            search_query=None,
            should_relaunch_kpi_computation=None,
            starred=None,
            updated_at_gte=None,
            updated_at_lte=None,
            created_at_gte=None,
            created_at_lte=None,
            tag_ids=None,
        ),
        fields=("id", "title", "jsonInterface", "inputType"),
        options=QueryOptions(disable_tqdm=None, first=None, skip=0),
    )

    # Then
    assert isinstance(retrieved_projects, GeneratorType)
    assert list(retrieved_projects) == kili_projects


def test_given_a_project_when_update_its_properties_then_it_updates_project_props(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    def mocked_update_properties_in_project(
        project_id: ProjectId,
        project_data: ProjectDataKiliAPIGatewayInput,
        fields: ListOrTuple[str],
    ):
        return {field: f"{field}_value" for field in fields}

    kili_api_gateway.update_properties_in_project.side_effect = mocked_update_properties_in_project

    # When
    project = ProjectUseCases(kili_api_gateway).update_properties_in_project(
        project_id=ProjectId("fake_proj_id"),
        title="new_title",
        can_navigate_between_assets=None,
        can_skip_asset=None,
        compliance_tags=None,
        consensus_mark=None,
        consensus_tot_coverage=None,
        description=None,
        honeypot_mark=None,
        instructions=None,
        json_interface=None,
        min_consensus_size=None,
        review_coverage=None,
        should_relaunch_kpi_computation=None,
        use_honeypot=None,
        metadata_types=None,
    )

    # Then
    assert "id" in project
    assert project == {"title": "title_value", "id": "id_value"}


@pytest.mark.parametrize(
    ("workflow_version", "workflow"),
    [("V2", "multi-step workflow"), ("V3", "multi-group workflow")],
)
@pytest.mark.parametrize(
    ("settings", "refused", "instead"),
    [
        (
            {"review_coverage": 30, "use_honeypot": True},
            "`review_coverage` and `use_honeypot` cannot be set",
            "`update_review_step_properties(project_id=..., step_name=..., step_coverage=...)`;"
            " the honeypot of a step with `update_labeling_step_properties(",
        ),
        ({"review_coverage": 30}, "`review_coverage` cannot be set", "step_coverage=...)`."),
        ({"review_coverage": 0}, "`review_coverage` cannot be set", "step_coverage=...)`."),
        ({"use_honeypot": True}, "`use_honeypot` cannot be set", "use_honeypot=...)`"),
        ({"use_honeypot": False}, "`use_honeypot` cannot be set", "use_honeypot=...)`"),
    ],
)
def test_given_a_project_with_step_settings_when_setting_review_coverage_or_honeypot_on_it_then_it_is_refused(
    kili_api_gateway: KiliAPIGateway,
    workflow_version: str,
    workflow: str,
    settings: dict,
    refused: str,
    instead: str,
):
    # Given
    kili_api_gateway.get_project.return_value = {"workflowVersion": workflow_version}

    # When / Then
    with pytest.raises(DeprecatedArgumentError, match="cannot be set") as error:
        ProjectUseCases(kili_api_gateway).update_properties_in_project(
            project_id=ProjectId("fake_proj_id"), title="new_title", **settings
        )
    assert str(error.value).startswith(
        f"{refused} on project fake_proj_id: it uses a {workflow}"
        f" (`workflowVersion` is `{workflow_version}`),"
    )
    assert "Nothing was changed." in str(error.value)
    assert instead in str(error.value)
    kili_api_gateway.get_project.assert_called_once_with(
        project_id="fake_proj_id", fields=["workflowVersion"]
    )
    kili_api_gateway.update_properties_in_project.assert_not_called()


def test_given_a_legacy_workflow_project_when_setting_review_coverage_and_honeypot_then_they_are_sent(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.get_project.return_value = {"workflowVersion": "V1"}

    # When
    ProjectUseCases(kili_api_gateway).update_properties_in_project(
        project_id=ProjectId("fake_proj_id"), review_coverage=30, use_honeypot=True
    )

    # Then
    project_id, project_data, fields = kili_api_gateway.update_properties_in_project.call_args[0]
    assert project_id == "fake_proj_id"
    assert (project_data.review_coverage, project_data.use_honeypot) == (30, True)
    assert set(fields) == {"reviewCoverage", "useHoneyPot", "id"}


def test_given_a_project_when_updating_neither_review_coverage_nor_honeypot_then_its_workflow_is_not_read(
    kili_api_gateway: KiliAPIGateway,
):
    # When
    ProjectUseCases(kili_api_gateway).update_properties_in_project(
        project_id=ProjectId("fake_proj_id"), title="new_title", consensus_tot_coverage=10
    )

    # Then
    kili_api_gateway.get_project.assert_not_called()
    kili_api_gateway.update_properties_in_project.assert_called_once()


def test_given_an_out_of_range_review_coverage_then_its_range_is_refused_before_the_workflow_is_read(
    kili_api_gateway: KiliAPIGateway,
):
    # When / Then
    with pytest.raises(ValueError, match="must be comprised between 0 and 100"):
        ProjectUseCases(kili_api_gateway).update_properties_in_project(
            project_id=ProjectId("fake_proj_id"), review_coverage=101
        )
    kili_api_gateway.get_project.assert_not_called()
