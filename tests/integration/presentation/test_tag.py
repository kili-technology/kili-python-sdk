import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.tag.operations import (
    GQL_CHECK_TAG,
    GQL_DELETE_TAG,
    get_list_tags_by_org_query,
    get_list_tags_by_project_query,
)
from kili.presentation.client.tag import TagClientMethods


def test_when_fetching_org_tags_then_i_get_tags(mocker: pytest_mock.MockerFixture):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )

    # When
    kili.tags()

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_list_tags_by_org_query(fragment=" id organizationId label checkedForProjects")
    )


def test_when_fetching_project_tags_then_i_get_tags(mocker: pytest_mock.MockerFixture):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )

    # When
    kili.tags(project_id="fake_proj_id")

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_list_tags_by_project_query(fragment=" id organizationId label checkedForProjects"),
        {"projectId": "fake_proj_id"},
    )


def test_given_tags_when_i_tag_project_with_tag_ids_then_it_is_tagged(
    mocker: pytest_mock.MockerFixture,
):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1", "checkedForProjects": []},
        {"id": "tag2_id", "label": "tag2", "checkedForProjects": []},
    ]
    kili.kili_api_gateway.list_tags_by_org = mocker.MagicMock(return_value=tags)

    # When
    kili.tag_project(project_id="fake_proj_id", tag_ids=["tag1_id", "tag2_id"])

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_with(
        GQL_CHECK_TAG, {"data": {"tagId": "tag2_id", "projectId": "fake_proj_id"}}
    )


def test_given_tags_when_i_tag_project_with_tag_labels_then_it_is_tagged(
    mocker: pytest_mock.MockerFixture,
):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1", "checkedForProjects": []},
        {"id": "tag2_id", "label": "tag2", "checkedForProjects": []},
    ]
    kili.kili_api_gateway.list_tags_by_org = mocker.MagicMock(return_value=tags)

    # When
    kili.tag_project(project_id="fake_proj_id", tags=["tag1", "tag2"])

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_with(
        GQL_CHECK_TAG, {"data": {"tagId": "tag2_id", "projectId": "fake_proj_id"}}
    )


def test_given_tags_when_i_untag_all_project_tags_then_it_removes_all_tags(
    mocker: pytest_mock.MockerFixture,
):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    kili.kili_api_gateway.uncheck_tag = mocker.MagicMock()
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili.kili_api_gateway.list_tags_by_project = mocker.MagicMock(return_value=tags)

    # When
    kili.untag_project(project_id="fake_proj_id", all=True)

    # Then
    assert kili.kili_api_gateway.uncheck_tag.call_count == len(tags)
    kili.kili_api_gateway.uncheck_tag.assert_called_with(
        project_id="fake_proj_id", tag_id="tag2_id"
    )


def test_given_tags_when_i_delete_them_then_it_works(
    mocker: pytest_mock.MockerFixture,
):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )

    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili.kili_api_gateway.list_tags_by_org = mocker.MagicMock(return_value=tags)

    # When
    kili.delete_tag(tag_name="tag1")

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        GQL_DELETE_TAG, {"tagId": "tag1_id"}
    )
