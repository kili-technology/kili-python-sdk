import uuid

import pytest

from kili.client import Kili


@pytest.fixture()
def project_id(kili: Kili):
    project_id = kili.create_project(
        input_type="TEXT", json_interface={"jobs": {}}, title="test_tags.py e2e admin SDK"
    )["id"]

    yield project_id

    kili.delete_project(project_id)


def test_given_org_with_tags_when_i_update_tag_then_it_is_updated(kili: Kili):
    # Given
    org_tags = kili.tags(fields=("label",))
    assert len(org_tags) > 0, "Organization has no tags"
    tag_to_update = next(tag for tag in org_tags if tag["label"])
    prev_tag_name = tag_to_update["label"]

    # When
    new_tag_name = str(uuid.uuid4())
    kili.update_tag(tag_name=prev_tag_name, new_tag_name=new_tag_name)

    # Then
    org_tags = kili.tags(fields=("label",))
    assert len(org_tags) > 0, "Organization has no tags"
    assert new_tag_name in [tag["label"] for tag in org_tags]

    # Cleanup
    kili.update_tag(tag_name=new_tag_name, new_tag_name=prev_tag_name)
