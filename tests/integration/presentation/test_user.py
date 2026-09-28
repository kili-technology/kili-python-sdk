from collections.abc import Generator
from unittest.mock import call

import pytest
from typeguard import check_type

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.queries import PaginatedGraphQLQuery
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.user.operations import (
    GQL_COUNT_USERS,
    get_update_user_mutation,
    get_users_query,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.presentation.client.user import UserClientMethods
from kili.use_cases.user import UserUseCases


@pytest.mark.parametrize(
    ("args", "kwargs", "expected_return_type"),
    [
        ((), {}, list[dict]),
        ((), {"as_generator": True}, Generator[dict, None, None]),
        ((), {"as_generator": False}, list[dict]),
        ((), {"email": "test@kili.com", "as_generator": False}, list[dict]),
    ],
)
def test_given_users_query_when_i_call_it_i_get_correct_return_type(
    kili_api_gateway: KiliAPIGateway, mocker, args, kwargs, expected_return_type
):
    # Given
    mocker.patch.object(
        UserUseCases,
        "list_users",
        return_value=(u for u in [{"id": "fake_user_id_1"}, {"id": "fake_user_id_2"}]),
    )
    kili = UserClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    result = kili.users(*args, **kwargs)

    # Then
    check_type(result, expected_return_type)
    assert list(result) == [{"id": "fake_user_id_1"}, {"id": "fake_user_id_2"}]


def _user_where(**overrides) -> dict:
    return {
        "activated": None,
        "email": None,
        "id": None,
        "idIn": None,
        "organization": {"id": None},
        **overrides,
    }


@pytest.fixture()
def kili_with_real_gateway(graphql_client: GraphQLClient, http_client: HttpClient):
    kili = UserClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)
    return kili


@pytest.mark.parametrize("as_generator", [False, True])
@pytest.mark.parametrize("activated", [True, False, None])
def test_given_users_query_when_i_filter_on_activated_then_the_where_sent_carries_it(
    kili_with_real_gateway: UserClientMethods,
    graphql_client: GraphQLClient,
    mocker,
    activated,
    as_generator,
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"email": "fake_email"}]}

    # When
    result = kili_with_real_gateway.users(
        fields=("email",), disable_tqdm=True, activated=activated, as_generator=as_generator
    )

    # Then
    assert list(result) == [{"email": "fake_email"}]
    graphql_client.execute.assert_called_once_with(
        get_users_query(" email"),
        {"where": _user_where(activated=activated), "skip": 0, "first": 1},
    )


def test_given_users_query_when_i_do_not_pass_activated_then_everybody_is_asked_for(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient, mocker
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"email": "fake_email"}]}

    # When
    kili_with_real_gateway.users(fields=("email",), disable_tqdm=True)

    # Then
    graphql_client.execute.assert_called_once_with(
        get_users_query(" email"), {"where": _user_where(), "skip": 0, "first": 1}
    )


def test_given_users_query_when_i_filter_on_activated_then_the_paginated_count_gets_the_same_where(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient
):
    # Given: the paginator first counts, then fetches; nothing is stubbed
    graphql_client.execute.side_effect = [
        {"data": 2},
        {"data": [{"email": "fake_email_1"}, {"email": "fake_email_2"}]},
    ]

    # When
    result = kili_with_real_gateway.users(fields=("email",), disable_tqdm=True, activated=False)

    # Then
    assert result == [{"email": "fake_email_1"}, {"email": "fake_email_2"}]
    where = _user_where(activated=False)
    assert graphql_client.execute.call_args_list == [
        call(GQL_COUNT_USERS, {"where": where}),
        call(get_users_query(" email"), {"where": where, "skip": 0, "first": 2}),
    ]


def test_given_users_query_when_i_combine_activated_with_the_other_filters_then_all_are_sent(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient, mocker
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"email": "fake_email"}]}

    # When
    kili_with_real_gateway.users(
        email="fake_email",
        organization_id="fake_org_id",
        fields=("email",),
        disable_tqdm=True,
        activated=False,
    )

    # Then
    graphql_client.execute.assert_called_once_with(
        get_users_query(" email"),
        {
            "where": _user_where(
                activated=False, email="fake_email", organization={"id": "fake_org_id"}
            ),
            "skip": 0,
            "first": 1,
        },
    )


@pytest.mark.parametrize("activated", [True, False, None])
def test_given_count_users_when_i_filter_on_activated_then_the_where_sent_carries_it(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient, activated
):
    # Given
    graphql_client.execute.return_value = {"data": 3}

    # When
    result = kili_with_real_gateway.count_users(activated=activated)

    # Then
    assert result == 3
    graphql_client.execute.assert_called_once_with(
        GQL_COUNT_USERS, {"where": _user_where(activated=activated)}
    )


def test_given_count_users_when_i_do_not_pass_activated_then_everybody_is_counted(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient
):
    # Given
    graphql_client.execute.return_value = {"data": 3}

    # When
    result = kili_with_real_gateway.count_users()

    # Then
    assert result == 3
    graphql_client.execute.assert_called_once_with(GQL_COUNT_USERS, {"where": _user_where()})


def test_given_count_users_when_i_combine_activated_with_the_other_filters_then_all_are_sent(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient
):
    # Given
    graphql_client.execute.return_value = {"data": 1}

    # When
    result = kili_with_real_gateway.count_users(
        organization_id="fake_org_id", email="fake_email", activated=True
    )

    # Then
    assert result == 1
    graphql_client.execute.assert_called_once_with(
        GQL_COUNT_USERS,
        {
            "where": _user_where(
                activated=True, email="fake_email", organization={"id": "fake_org_id"}
            )
        },
    )


@pytest.mark.parametrize("activated", [True, False])
def test_given_a_user_when_i_change_its_activation_then_the_lookup_does_not_filter_on_it(
    kili_with_real_gateway: UserClientMethods, graphql_client: GraphQLClient, activated
):
    # Given
    graphql_client.execute.return_value = {"data": {"id": "fake_user_id"}}

    # When
    kili_with_real_gateway.update_properties_in_user(email="fake_email", activated=activated)

    # Then: a deactivated user must still be found by its email to be reactivated
    graphql_client.execute.assert_called_once()
    query, variables = graphql_client.execute.call_args.args
    assert query == get_update_user_mutation(" id")
    assert variables["where"] == _user_where(email="fake_email")
    assert variables["data"]["activated"] is activated
