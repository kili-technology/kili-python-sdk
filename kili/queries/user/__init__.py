"""User queries."""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from ...types import User
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import GQL_USERS_COUNT, gql_users


class QueriesUser:
    """Set of User queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(["v1", "v2"])
    @typechecked
    def users(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["email", "id", "firstname", "lastname"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of users given a set of criteria

        Args:
            api_key: Query an user by its API Key
            email: Email of the user
            organization_id: Identifier of the user's organization
            fields: All the fields to request among the possible fields for the users.
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#user) for all possible fields.
            first: Maximum number of users to return
            skip: Number of skipped users (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the users is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            ```
            # List all users in my organization
            >>> organization = kili.organizations()
            >>> organization_id = organizations[0]['id]
            >>> kili.users(organization_id=organization_id)
            ```
        """

        count_args = {"organization_id": organization_id}
        disable_tqdm = disable_tqdm or as_generator or (api_key or email) is not None
        payload_query = {
            "where": {
                "apiKey": api_key,
                "email": email,
                "organization": {
                    "id": organization_id,
                },
            }
        }

        users_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_users,
            count_args,
            self._query_users,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return users_generator
        return list(users_generator)

    def _query_users(self, skip: int, first: int, payload: dict, fields: List[str]):

        payload.update({"skip": skip, "first": first})
        _gql_users = gql_users(fragment_builder(fields, User))
        result = self.auth.client.execute(_gql_users, payload)
        return format_result("data", result)

    @Compatible(["v1", "v2"])
    @typechecked
    def count_users(self, organization_id: Optional[str] = None) -> int:
        """Get user count based on a set of constraints.

        Args:
            organization_id: Identifier of the user's organization

        Returns:
            The number of organizations with the parameters provided
        """
        variables = {
            "where": {
                "organization": {
                    "id": organization_id,
                }
            }
        }
        result = self.auth.client.execute(GQL_USERS_COUNT, variables)
        return format_result("data", result)
