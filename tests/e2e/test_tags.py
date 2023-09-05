import pytest

from kili.client import Kili


@pytest.fixture()
def project_id(kili: Kili):
    project_id = kili.create_project(
        input_type="TEXT", json_interface={"jobs": {}}, title="test_tags.py e2e SDK"
    )["id"]

    yield project_id

    kili.delete_project(project_id)


def test_given_org_tags_when_i_tag_project_it_tags_it(kili: Kili, project_id: str):
    # Given
    org_tags = kili.tags(fields=("label",))
    assert len(org_tags) > 0, "Organization has no tags"
    tags_to_add_to_project = org_tags[:3]
    tags_to_add_to_project_label = [tag["label"] for tag in tags_to_add_to_project]

    # When
    kili.tag_project(project_id, tags=tags_to_add_to_project_label)

    # Then
    project_tags = kili.tags(project_id=project_id, fields=("label",))
    assert sorted([tag["label"] for tag in project_tags]) == sorted(tags_to_add_to_project_label)


@pytest.fixture()
def project_with_tags_id(project_id: str, kili: Kili):
    org_tags = kili.tags(fields=("label",))
    assert len(org_tags) > 0, "Organization has no tags"
    tag_to_add_to_project = org_tags[0]["label"]
    kili.tag_project(project_id, tags=(tag_to_add_to_project,))

    yield project_id

    # kili.delete_project(project_id)  # project is deleted in project_id fixture


def test_given_project_with_tags_when_i_call_untag_project_then_it_removes_one_tag(
    kili: Kili, project_with_tags_id: str
):
    # Given
    tags_of_project = kili.tags(project_id=project_with_tags_id, fields=("label",))
    assert len(tags_of_project) > 0, "Project has no tags"
    nb_tags_in_project_before = len(tags_of_project)
    tag_to_delete = tags_of_project[0]["label"]

    # When
    kili.untag_project(project_with_tags_id, tags=(tag_to_delete,))

    # Then
    project_tags = kili.tags(project_id=project_with_tags_id, fields=("label",))
    nb_tags_in_project_after = len(project_tags)
    assert nb_tags_in_project_after == nb_tags_in_project_before - 1
    assert not any(tag["label"] == tag_to_delete for tag in project_tags)


def test_given_project_with_tags_when_i_call_untag_project_then_it_removes_all_tags(
    kili: Kili, project_with_tags_id: str
):
    # Given
    tags_of_project = kili.tags(project_id=project_with_tags_id, fields=("id",))
    assert len(tags_of_project) > 0, "Project has no tags"

    # When
    kili.untag_project(project_with_tags_id, all=True)

    # Then
    project_tags = kili.tags(project_id=project_with_tags_id, fields=("id",))
    assert len(project_tags) == 0
