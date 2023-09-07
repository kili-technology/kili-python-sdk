from types import GeneratorType

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectFilters
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
        first=None,
        skip=0,
        disable_tqdm=None,
    )

    # Then
    assert isinstance(retrieved_projects, GeneratorType)
    assert list(retrieved_projects) == kili_projects
