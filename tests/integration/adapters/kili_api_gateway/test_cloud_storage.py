from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.cloud_storage import (
    DataConnectionComputeDifferencesKiliAPIGatewayInput,
    DataIntegrationFilters,
)
from kili.adapters.kili_api_gateway.cloud_storage.operations import (
    GQL_COUNT_DATA_INTEGRATIONS,
    get_compute_data_connection_differences_mutation,
)
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.cloud_storage import DataConnectionId, DataIntegrationId


def test_given_gateway_when_calling_compute_diff_then_it_works(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    gateway.compute_data_connection_differences(
        data_connection_id=DataConnectionId("fake_data_con_id"), data=None, fields=("id",)
    )

    # Then
    gateway.graphql_client.execute.assert_called_once_with(
        get_compute_data_connection_differences_mutation(" id"),
        {"where": {"id": "fake_data_con_id"}},
    )


def test_given_gateway_when_calling_compute_diff_with_data_then_it_works(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    gateway.compute_data_connection_differences(
        data_connection_id=DataConnectionId("fake_data_con_id"),
        data=DataConnectionComputeDifferencesKiliAPIGatewayInput(
            blob_paths=["1.jpg", "2.jpg"],
            warnings=["warning1", "warning2"],
            content_types=["image/jpeg", "image/jpeg"],
        ),
        fields=("id",),
    )

    # Then
    gateway.graphql_client.execute.assert_called_once_with(
        get_compute_data_connection_differences_mutation(" id"),
        {
            "where": {"id": "fake_data_con_id"},
            "data": {
                "blobPaths": ["1.jpg", "2.jpg"],
                "warnings": ["warning1", "warning2"],
                "contentTypes": ["image/jpeg", "image/jpeg"],
            },
        },
    )


def test_given_gateway_when_calling_count_data_integrations_then_it_works(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    gateway.count_data_integrations(DataIntegrationFilters(id=DataIntegrationId("fake_id")))

    # Then
    gateway.graphql_client.execute.assert_called_once_with(
        GQL_COUNT_DATA_INTEGRATIONS,
        {
            "where": {
                "status": None,
                "id": "fake_id",
                "name": None,
                "organizationId": None,
                "platform": None,
            }
        },
    )
