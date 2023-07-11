import uuid

import pytest

from kili.client import Kili


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture
def projects_uuid(kili: Kili):
    projects_uuid = str(uuid.uuid4())
    proj_id_archived = kili.create_project(
        input_type="TEXT", json_interface={}, title="test_projects.py archived" + projects_uuid
    )["id"]
    proj_id_not_archived_1 = kili.create_project(
        input_type="TEXT",
        json_interface={},
        title="test_projects.py not archived 1" + projects_uuid,
    )["id"]
    proj_id_not_archived_2 = kili.create_project(
        input_type="TEXT",
        json_interface={},
        title="test_projects.py not archived 2" + projects_uuid,
    )["id"]

    kili.archive_project(proj_id_archived)

    yield projects_uuid

    kili.delete_project(proj_id_archived)
    kili.delete_project(proj_id_not_archived_1)
    kili.delete_project(proj_id_not_archived_2)


def test_projects_query_archived_project(kili: Kili, projects_uuid: str):
    assert (
        len(kili.projects(fields=["id"], search_query=projects_uuid))
        == kili.count_projects(search_query=projects_uuid)
        == 3
    )
    assert (
        len(kili.projects(fields=["id"], search_query=projects_uuid, archived=False))
        == kili.count_projects(search_query=projects_uuid, archived=False)
        == 2
    )
    assert (
        len(kili.projects(fields=["id"], search_query=projects_uuid, archived=True))
        == kili.count_projects(search_query=projects_uuid, archived=True)
        == 1
    )
