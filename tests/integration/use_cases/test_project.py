from types import GeneratorType

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.types import ProjectDataKiliAPIGatewayInput
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.project.project import ProjectUseCases


def test_when_create_project_it_works(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.create_project.return_value = "fake_project_id"

    # When
    project_id = ProjectUseCases(kili_api_gateway).create_project(
        input_type="TEXT",
        json_interface={},
        title="test",
        description="description",
        project_type=None,
        compliance_tags=None,
    )

    # Then
    assert project_id == "fake_project_id"


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
        use_auto_assign=None,
        metadata_types=None,
    )

    # Then
    assert "id" in project
    assert project == {"title": "title_value", "id": "id_value"}
