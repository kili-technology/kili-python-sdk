"""Integration tests for TagView objects returned by the tags namespace."""

import pytest

from kili.domain_v2.tag import TagView
from tests_v2 import assert_is_view, assert_view_has_dict_compatibility, assert_view_property_access


@pytest.mark.integration()
def test_list_returns_tag_views(kili_client):
    """Test that tags.list() returns TagView objects."""
    tags = kili_client.tags.list()

    assert isinstance(tags, list), "tags.list() should return a list"

    if not tags:
        pytest.skip("No tags available for testing")

    for tag in tags:
        assert_is_view(tag, TagView)
        assert hasattr(tag, "id")
        assert hasattr(tag, "label")


@pytest.mark.integration()
def test_tag_view_properties(kili_client):
    """Test that TagView provides access to all expected properties."""
    tags = kili_client.tags.list()

    if not tags:
        pytest.skip("No tags available for testing")

    tag = tags[0]
    assert_is_view(tag, TagView)

    assert_view_property_access(tag, "id")
    assert_view_property_access(tag, "label")
    assert_view_property_access(tag, "organization_id")
    assert_view_property_access(tag, "display_name")

    assert tag.id, "Tag id should not be empty"
    assert tag.display_name, "Tag display_name should not be empty"


@pytest.mark.integration()
def test_tag_view_dict_compatibility(kili_client):
    """Test that TagView maintains backward compatibility via to_dict()."""
    tags = kili_client.tags.list()

    if not tags:
        pytest.skip("No tags available for testing")

    tag = tags[0]
    assert_is_view(tag, TagView)
    assert_view_has_dict_compatibility(tag)

    tag_dict = tag.to_dict()
    assert isinstance(tag_dict, dict), "to_dict() should return a dictionary"
    assert "id" in tag_dict, "Dictionary should have 'id' key"
    assert tag_dict is tag._data, "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_tag_view_with_project_filter(kili_client):
    """Test listing tags for a specific project."""
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    project_id = projects[0].id
    project_tags = kili_client.tags.list(project_id=project_id)

    assert isinstance(project_tags, list), "Should return a list"

    for tag in project_tags:
        assert_is_view(tag, TagView)


@pytest.mark.integration()
def test_tag_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    tags = kili_client.tags.list()
    assert isinstance(tags, list), "Should return a list even when no results"


@pytest.mark.integration()
def test_tag_view_with_fields_parameter(kili_client):
    """Test that TagView works correctly with custom fields parameter."""
    tags = kili_client.tags.list(fields=["id", "label"])

    if not tags:
        pytest.skip("No tags available for testing")

    tag = tags[0]
    assert_is_view(tag, TagView)
    assert_view_property_access(tag, "id")
    assert_view_property_access(tag, "label")
