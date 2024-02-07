"""Mixin extending Kili API Gateway class with User related operations."""

from typing import Dict, Generator

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
    fragment_builder,
)
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter

from .mappers import create_user_data_mapper, update_user_data_mapper, user_where_mapper
from .operations import (
    GQL_COUNT_USERS,
    get_create_user_mutation,
    get_current_user_query,
    get_update_password_mutation,
    get_update_user_mutation,
    get_users_query,
)
from .types import CreateUserDataKiliGatewayInput, UserDataKiliGatewayInput


class UserOperationMixin(BaseOperationMixin):
    """GraphQL Mixin extending GraphQL Gateway class with User related operations."""

    def list_users(
        self, user_filters: UserFilter, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """Return a generator of users that match the filter."""
        fragment = fragment_builder(fields)
        query = get_users_query(fragment)
        where = user_where_mapper(filters=user_filters)
        return PaginatedGraphQLQuery(self.graphql_client).execute_query_from_paginated_call(
            query, where, options, "Retrieving users", GQL_COUNT_USERS
        )

    def count_users(self, user_filters: UserFilter) -> int:
        """Return the number of users that match the filter."""
        variables = {"where": user_where_mapper(user_filters)}
        result = self.graphql_client.execute(GQL_COUNT_USERS, variables)
        return result["data"]

    def get_current_user(self, fields: ListOrTuple[str]) -> Dict:
        """Return the current user."""
        fragment = fragment_builder(fields)
        query = get_current_user_query(fragment=fragment)
        result = self.graphql_client.execute(query)
        return result["data"]

    def create_user(self, data: CreateUserDataKiliGatewayInput, fields: ListOrTuple[str]) -> Dict:
        """Create a user."""
        fragment = fragment_builder(fields)
        query = get_create_user_mutation(fragment)
        variables = {"data": create_user_data_mapper(data)}
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def update_password(
        self,
        old_password: str,
        new_password_1: str,
        new_password_2: str,
        user_filter: UserFilter,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update user password."""
        fragment = fragment_builder(fields)
        query = get_update_password_mutation(fragment)
        variables = {
            "data": {
                "oldPassword": old_password,
                "newPassword1": new_password_1,
                "newPassword2": new_password_2,
            },
            "where": user_where_mapper(filters=user_filter),
        }
        result = self.graphql_client.execute(query, variables)
        return result["data"]

    def update_user(
        self, user_filter: UserFilter, data: UserDataKiliGatewayInput, fields: ListOrTuple[str]
    ) -> Dict:
        """Update a user."""
        fragment = fragment_builder(fields)
        query = get_update_user_mutation(fragment)
        variables = {
            "data": update_user_data_mapper(data),
            "where": user_where_mapper(filters=user_filter),
        }
        result = self.graphql_client.execute(query, variables)
        return result["data"]
