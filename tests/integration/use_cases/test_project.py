from types import GeneratorType

import pytest

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.types import ProjectDataKiliAPIGatewayInput
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
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
        project_type=None,
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
        match="Arguments `input_type` and `json_interface` must be set\n                if no `project_id` is providen.",
    ):
        project_use_cases.create_project(
            title="test",
            description="description",
            project_type=None,
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
        project_type=None,
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
            project_type=None,
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
        input_type=None,
        json_interface=None,
        min_consensus_size=None,
        number_of_assets=None,
        number_of_skipped_assets=None,
        number_of_remaining_assets=None,
        number_of_reviewed_assets=None,
        review_coverage=None,
        should_relaunch_kpi_computation=None,
        use_honeypot=None,
        metadata_types=None,
    )

    # Then
    assert "id" in project
    assert project == {"title": "title_value", "id": "id_value"}
