import pytest

from kili.client import Kili


@pytest.fixture()
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def project_id(kili: Kili):
    project_id = kili.create_project(
        input_type="TEXT", json_interface={"jobs": {}}, title="test_tags.py e2e SDK"
    )["id"]

    yield project_id

    kili.delete_project(project_id)


def test_tag_project(kili: Kili, project_id: str):
    # Given
    org_tags = kili.tags()
    tags_to_add_to_project = org_tags[:3]
    tags_to_add_to_project_label = [tag["label"] for tag in tags_to_add_to_project]

    # When
    kili.tag_project(project_id, tags=tags_to_add_to_project_label)

    # Then
    project_tags = kili.tags(project_id=project_id)
    assert sorted([tag["label"] for tag in project_tags]) == sorted(tags_to_add_to_project_label)
