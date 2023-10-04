import uuid

import pytest

from kili.client import Kili


@pytest.fixture()
def project_name(kili: Kili):
    project_name = "e2e test_create_project " + str(uuid.uuid4())

    yield project_name

    project_id = kili.projects(search_query=f"%{project_name}%", first=1)[0]["id"]
    kili.delete_project(project_id)


def test_create_project(project_name: str, kili: Kili):
    _ = kili.create_project(input_type="TEXT", json_interface={}, title=project_name)


@pytest.fixture()
def projects_uuid(kili: Kili):
    projects_uuid = str(uuid.uuid4())
    proj_id_archived = kili.create_project(
        input_type="TEXT", json_interface={}, title="test_projects.py archived " + projects_uuid
    )["id"]
    proj_id_not_archived_1 = kili.create_project(
        input_type="TEXT",
        json_interface={},
        title="test_projects.py not archived 1 " + projects_uuid,
    )["id"]
    proj_id_not_archived_2 = kili.create_project(
        input_type="TEXT",
        json_interface={},
        title="test_projects.py not archived 2 " + projects_uuid,
    )["id"]

    kili.archive_project(proj_id_archived)

    yield projects_uuid

    kili.delete_project(proj_id_archived)
    kili.delete_project(proj_id_not_archived_1)
    kili.delete_project(proj_id_not_archived_2)


def test_projects_query_archived_project(kili: Kili, projects_uuid: str):
    search_query = f"%{projects_uuid}"

    # should have 2 projects not archived
    assert kili.count_projects(search_query=search_query, archived=False) == 2
    projects = kili.projects(fields=["id", "title"], search_query=search_query, archived=False)
    assert len(projects) == 2

    # should have 1 project archived
    assert kili.count_projects(search_query=search_query, archived=True) == 1
    projects = kili.projects(fields=["id", "title"], search_query=search_query, archived=True)
    assert len(projects) == 1

    # should have 3 projects in total
    assert kili.count_projects(search_query=search_query) == 3
    projects = kili.projects(fields=["id", "title"], search_query=search_query)
    assert len(projects) == 3


def test_given_projects_when_i_query_projects_with_filters_then_i_get_projects(
    projects_uuid: str, kili: Kili
):
    # Given

    # When
    retrieved_projects = kili.projects(search_query=f"%{projects_uuid}", fields=("jsonInterface",))

    # Then
    assert len(retrieved_projects) == 3
    # make sure jsoninterface is serialized (it's a GraphQL string type field)
    assert all(isinstance(proj["jsonInterface"], dict) for proj in retrieved_projects)
