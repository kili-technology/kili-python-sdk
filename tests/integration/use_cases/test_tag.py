import pytest

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.use_cases.tag import TagUseCases


def test_when_get_tags_of_organization_then_i_get_tags(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    fetched_tags = TagUseCases(kili_api_gateway).get_tags_of_organization(fields=["id", "label"])

    # Then
    assert fetched_tags == tags


def test_when_get_tags_of_project_then_i_get_tags(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_project.return_value = tags

    # When
    fetched_tags = TagUseCases(kili_api_gateway).get_tags_of_project(
        project_id="fake_proj_id", fields=["id", "label"]
    )

    # Then
    assert fetched_tags == tags


def test_when_tagging_project_then_it_tags_the_project(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.check_tag.side_effect = lambda project_id, tag_id: tag_id
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    applied_tags = TagUseCases(kili_api_gateway).tag_project(
        project_id="fake_proj_id", tags=["tag1", "tag2_id"], disable_tqdm=True
    )

    # Then
    assert applied_tags == [
        {"id": "tag1_id"},
        {"id": "tag2_id"},
    ]


def test_when_tagging_project_with_invalid_organization_tag_then_it_crashes(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    tag_use_cases = TagUseCases(kili_api_gateway)
    with pytest.raises(
        ValueError, match="Tag this_tag_does_not_exist_it_is_fake not found in organization"
    ):
        tag_use_cases.tag_project(
            project_id="fake_proj_id",
            tags=["this_tag_does_not_exist_it_is_fake"],
            disable_tqdm=True,
        )
