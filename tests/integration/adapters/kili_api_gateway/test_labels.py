import pytest_mock

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
)
from kili.adapters.kili_api_gateway.label.operations import get_labels_query
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetExternalId, AssetFilters
from kili.domain.label import LabelFilters, LabelId
from kili.domain.project import ProjectFilters, ProjectId


def test_given_kili_gateway_when_querying_labels__it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient, mocker: pytest_mock.MockerFixture
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"id": "fake_label_id"}]}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    labels_gen = kili_gateway.list_labels(
        LabelFilters(
            id=LabelId("fake_label_id"),
            project=ProjectFilters(id=ProjectId("fake_proj_id")),
            asset=AssetFilters(
                external_id_in=[AssetExternalId("fake_asset_id")],
                project_id=ProjectId("fake_proj_id"),
            ),
        ),
        fields=("id",),
        options=QueryOptions(disable_tqdm=True),
    )
    _ = list(labels_gen)

    # Then
    cleaned_variables = GraphQLClient._remove_nullable_inputs(
        graphql_client.execute.call_args[0][1]
    )
    graphql_client.execute.assert_called_once_with(
        get_labels_query(" id"),
        graphql_client.execute.call_args[0][1],
    )
    assert cleaned_variables == {
        "where": {
            "id": "fake_label_id",
            "project": {"id": "fake_proj_id"},
            "asset": {
                "externalIdIn": ["fake_asset_id"],
                "project": {"id": "fake_proj_id"},
                "label": {},
                "issue": {},
            },
        },
        "first": 1,
        "skip": 0,
    }
