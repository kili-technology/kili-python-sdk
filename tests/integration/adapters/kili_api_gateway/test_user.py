import pytest_mock

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
)
from kili.adapters.kili_api_gateway.user.operations import (
    GQL_COUNT_USERS,
    get_create_user_mutation,
    get_current_user_query,
    get_update_user_mutation,
    get_users_query,
)
from kili.adapters.kili_api_gateway.user.types import (
    CreateUserDataKiliGatewayInput,
    UserDataKiliGatewayInput,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.user import UserFilter, UserId


def test_given_kili_gateway_when_querying_users_list_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient, mocker: pytest_mock.MockerFixture
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"email": "fake_email"}]}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    users_gen = kili_gateway.list_users(
        UserFilter(id=UserId("fake_user_id")),
        fields=("email",),
        options=QueryOptions(disable_tqdm=True),
    )
    _ = list(users_gen)

    # Then
    graphql_client.execute.assert_called_once_with(
        get_users_query(" email"),
        {
            "where": {
                "activated": None,
                "apiKey": None,
                "email": None,
                "id": "fake_user_id",
                "idIn": None,
                "organization": {"id": None},
            },
            "skip": 0,
            "first": 1,
        },
    )


def test_given_kili_gateway_when_querying_count_users_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    graphql_client.execute.return_value = {"data": 42}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    users_count = kili_gateway.count_users(UserFilter(id=UserId("fake_user_id")))

    # Then
    assert users_count == 42
    graphql_client.execute.assert_called_once_with(
        GQL_COUNT_USERS,
        {
            "activated": None,
            "apiKey": None,
            "email": None,
            "id": "fake_user_id",
            "idIn": None,
            "organization": {"id": None},
        },
    )


def test_given_kili_gateway_when_querying_current_users_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "current_user_id"}}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    current_user = kili_gateway.get_current_user(fields=("id",))

    # Then
    assert current_user == {"id": "current_user_id"}
    graphql_client.execute.assert_called_once_with(
        get_current_user_query(" id"),
    )


def test_given_kili_gateway_when_creating_user_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    _ = kili_gateway.create_user(
        fields=("id",),
        data=CreateUserDataKiliGatewayInput(
            email="fake@email.com",
            firstname="john",
            lastname="doe",
            password="fake_pass",
            organization_role="USER",
        ),
    )

    # Then
    graphql_client.execute.assert_called_once_with(
        get_create_user_mutation(" id"),
        {
            "email": "fake@email.com",
            "firstname": "john",
            "lastname": "doe",
            "password": "fake_pass",
            "organizationRole": "USER",
        },
    )


def test_given_kili_gateway_when_updating_user_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    _ = kili_gateway.update_user(
        user_filter=UserFilter(id="fake_user_id"),
        fields=("id",),
        data=UserDataKiliGatewayInput(organization_role="USER"),
    )

    # Then
    graphql_client.execute.assert_called_once_with(
        get_update_user_mutation(" id"),
        {
            "data": {
                "activated": None,
                "apiKey": None,
                "auth0Id": None,
                "email": None,
                "firstname": None,
                "hasCompletedLabelingTour": None,
                "hubspotSubscriptionStatus": None,
                "lastname": None,
                "organization": None,
                "organizationId": None,
                "organizationRole": "USER",
            },
            "where": {
                "activated": None,
                "apiKey": None,
                "email": None,
                "id": "fake_user_id",
                "idIn": None,
                "organization": {"id": None},
            },
        },
    )
