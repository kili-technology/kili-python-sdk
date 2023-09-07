from kili.adapters.kili_api_gateway import KiliAPIGateway
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
