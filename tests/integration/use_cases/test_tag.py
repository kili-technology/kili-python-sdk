import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.domain.tag import TagId
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
        project_id=ProjectId("fake_proj_id"), fields=["id", "label"]
    )

    # Then
    assert fetched_tags == tags


def test_given_tag_ids_when_tagging_project_then_it_tags_the_project(
    kili_api_gateway: KiliAPIGateway,
):
    kili_api_gateway.check_tag.side_effect = lambda project_id, tag_id: tag_id
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    applied_tags = TagUseCases(kili_api_gateway).tag_project(
        project_id=ProjectId("fake_proj_id"),
        tag_ids=[TagId("tag1_id"), TagId("tag2_id")],
        disable_tqdm=True,
    )

    # Then
    assert applied_tags == ["tag1_id", "tag2_id"]


def test_when_untagging_project_then_it_removes_some_tags(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.uncheck_tag.side_effect = lambda project_id, tag_id: tag_id
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_project.return_value = tags

    # When
    deleted_tags = TagUseCases(kili_api_gateway).untag_project(
        project_id=ProjectId("fake_proj_id"),
        tag_ids=[TagId("tag1_id"), TagId("tag2_id")],
        disable_tqdm=True,
    )

    # Then
    assert deleted_tags == ["tag1_id", "tag2_id"]


def test_given_tag_labels_when_i_convert_them_to_tag_ids_then_it_works(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    tag_ids = TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("tag2", "tag1"))

    # Then
    assert tag_ids == ["tag2_id", "tag1_id"]


@pytest.mark.parametrize("label", ["  Q4  ", "q4", "  q4 ", "\ufeffQ4", "Q4\u3000"])
def test_given_a_tag_when_i_name_it_with_other_case_or_outer_spaces_then_it_is_found(
    kili_api_gateway: KiliAPIGateway, label: str
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [
        {"id": "q4_id", "label": "Q4"},
        {"id": "other_id", "label": "Other"},
    ]

    # When
    tag_ids = TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=(label,))

    # Then
    assert tag_ids == ["q4_id"]


def test_given_a_tag_stored_with_outer_spaces_when_i_name_it_without_them_then_it_is_found(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [{"id": "padded_id", "label": "  Padded  "}]

    # When
    tag_ids = TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("padded",))

    # Then
    assert tag_ids == ["padded_id"]


def test_given_tags_the_backend_tells_apart_when_i_name_one_then_only_it_is_found(
    kili_api_gateway: KiliAPIGateway,
):
    # Given — the backend's trim() keeps U+001F, so "Q4\x1f" is another name than "Q4"
    kili_api_gateway.list_tags_by_org.return_value = [
        {"id": "q4_id", "label": "Q4"},
        {"id": "q4_unit_id", "label": "Q4\x1f"},
    ]

    # When
    tag_ids = TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("q4",))

    # Then
    assert tag_ids == ["q4_id"]


def test_given_two_names_of_one_tag_when_tagging_a_project_then_it_is_checked_once(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [{"id": "q4_id", "label": "Q4"}]
    kili_api_gateway.list_tags_by_project.return_value = []
    kili_api_gateway.check_tag.return_value = "q4_id"
    tag_use_cases = TagUseCases(kili_api_gateway)
    tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=("Q4", "q4"))

    # When
    tag_use_cases.tag_project(
        project_id=ProjectId("project_id"), tag_ids=tag_ids, disable_tqdm=True
    )

    # Then
    kili_api_gateway.check_tag.assert_called_once_with(project_id="project_id", tag_id="q4_id")


def test_given_old_duplicates_when_i_name_one_exactly_then_that_one_is_found(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [
        {"id": "upper_id", "label": "Urgent"},
        {"id": "lower_id", "label": "urgent"},
    ]

    # When
    tag_ids = TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("urgent", "Urgent"))

    # Then
    assert tag_ids == ["lower_id", "upper_id"]


def test_given_old_duplicates_when_i_name_neither_exactly_then_it_asks_for_ids(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [
        {"id": "upper_id", "label": "Urgent"},
        {"id": "lower_id", "label": "urgent"},
    ]

    # When / Then
    with pytest.raises(ValueError, match="Several tags with ids .* match the label `URGENT`"):
        TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("URGENT",))


def test_given_no_tag_of_that_name_when_i_name_it_then_it_crashes(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_tags_by_org.return_value = [{"id": "q4_id", "label": "Q4"}]

    # When / Then
    with pytest.raises(ValueError, match="Tag `Q4 bis` not found in organization"):
        TagUseCases(kili_api_gateway).get_tag_ids_from_labels(labels=("Q4 bis",))


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
            project_id=ProjectId("fake_proj_id"),
            tag_ids=[TagId("this_tag_does_not_exist_it_is_fake")],
            disable_tqdm=True,
        )


def test_given_existing_tag_when_i_update_its_name_then_it_works(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    TagUseCases(kili_api_gateway).update_tag(tag_id=TagId("tag1_id"), new_tag_name="tag1_new")

    # Then
    kili_api_gateway.update_tag.assert_called_once_with(tag_id="tag1_id", label="tag1_new")


def test_given_tag_to_delete_when_deleting_it_it_works(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
    ]
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    TagUseCases(kili_api_gateway).delete_tag(tag_id=TagId("tag1_id"))

    # Then
    kili_api_gateway.delete_tag.assert_called_once_with(tag_id="tag1_id")
