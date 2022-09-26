"""Project user queries."""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from ...types import ProjectUser
from ...utils.pagination import row_generator_from_paginated_calls
from .queries import GQL_PROJECT_USERS_COUNT, gql_project_users


class QueriesProjectUser:
    """Set of ProjectUser queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value,invalid-name
    @Compatible(["v1", "v2"])
    @typechecked
    def project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        organization_id: Optional[str] = None,
        fields: List[str] = [
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Return project users (possibly with their KPIs) that match a set of criteria


        Args:
            project_id: Identifier of the project
            email: Email of the user
            organization_id: Identifier of the user's organization
            fields: All the fields to request among the possible fields for the projectUsers
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectuser) for all possible fields.
            first: Maximum number of users to return
            skip: Number of project users to skip
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project users is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            ```
            # Retrieve consensus marks of all users in project
            >>> kili.project_users(project_id=project_id, fields=['consensusMark', 'user.email'])
            ```
        """
        count_args = {
            "email": email,
            "id": id,
            "organization_id": organization_id,
            "project_id": project_id,
        }
        disable_tqdm = disable_tqdm or as_generator
        payload_query = {
            "where": {
                "id": id,
                "project": {
                    "id": project_id,
                },
                "user": {
                    "email": email,
                    "organization": {
                        "id": organization_id,
                    },
                },
            }
        }

        project_users_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_project_users,
            count_args,
            self._query_project_users,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return project_users_generator
        return list(project_users_generator)

    def _query_project_users(self, skip: int, first: int, payload: dict, fields: List[str]):

        payload.update({"skip": skip, "first": first})
        _gql_project_users = gql_project_users(fragment_builder(fields, ProjectUser))
        result = self.auth.client.execute(_gql_project_users, payload)
        return format_result("data", result)

    # pylint: disable=invalid-name
    @typechecked
    def count_project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        organization_id: Optional[str] = None,
    ) -> int:
        """
        Counts the number of projects and their users that match a set of criteria

        Args:
            email: Email of the user
            organization_id: Identifier of the user's organization
            project_id: Identifier of the project

        Returns:
            The number of project users with the parameters provided
        """
        variables = {
            "where": {
                "id": id,
                "project": {
                    "id": project_id,
                },
                "user": {
                    "email": email,
                    "organization": {
                        "id": organization_id,
                    },
                },
            }
        }
        result = self.auth.client.execute(GQL_PROJECT_USERS_COUNT, variables)
        count = format_result("data", result)
        return count
