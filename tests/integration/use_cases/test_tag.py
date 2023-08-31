import pytest_mock

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.tag import TagClientMethods


def test_get_tags_by_org(mocker: pytest_mock.MockerFixture):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )

    kili.tags()

    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        query=(
            "query listTagsByOrg {\n            data: listTagsByOrg {\n                 id"
            " organizationId label checkedForProjects\n            }\n        }\n        "
        )
    )


def test_get_tags_by_project(mocker: pytest_mock.MockerFixture):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )

    kili.tags(project_id="fake_proj_id")

    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        "query listTagsByProject($projectId: ID!) {\n            data: listTagsByProject(projectId:"
        " $projectId) {\n                 id organizationId label checkedForProjects\n           "
        " }\n        }\n        ",
        {"projectId": "fake_proj_id"},
    )


def test_tag_project(mocker: pytest_mock.MockerFixture):
    kili = TagClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    kili.kili_api_gateway.list_tags_by_org = mocker.MagicMock(
        return_value=[
            {"id": "tag1_id", "label": "tag1"},
            {"id": "tag2_id", "label": "tag2"},
        ]
    )

    kili.tag_project(project_id="fake_proj_id", tags=["tag1", "tag2_id"])

    assert kili.kili_api_gateway.graphql_client.execute.call_count == 2
    kili.kili_api_gateway.graphql_client.execute.assert_called_with(
        "\nmutation checkTag($data: CheckedTagData!) {\n    data: checkTag(data: $data) {\n       "
        " id\n    }\n}\n",
        {"data": {"tagId": "tag2_id", "projectId": "fake_proj_id"}},
    )
