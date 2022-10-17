"""Project version queries."""

from typing import Generator, List, Optional, Union

from typeguard import typechecked

from kili.helpers import format_result, fragment_builder
from kili.queries.project_version.queries import (
    GQL_PROJECT_VERSION_COUNT,
    gql_project_version,
)
from kili.types import ProjectVersion as ProjectVersionType
from kili.utils.pagination import row_generator_from_paginated_calls


class QueriesProjectVersion:
    """Set of ProjectVersion queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def project_version(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: List[str] = ["createdAt", "id", "content", "name", "projectId"],
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of project versions respecting a set of criteria.

        Args:
            project_id: Filter on Id of project
            fields: All the fields to request among the possible fields for the project versions
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#projectVersions) for all possible fields.
            first: Number of project versions to query
            skip: Number of project versions to skip (they are ordered by their date
                of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project versions is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """
        count_args = {"project_id": project_id}
        disable_tqdm = disable_tqdm or as_generator
        payload_query = {
            "where": {
                "projectId": project_id,
            },
        }
        project_versions_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_project_versions,
            count_args,
            self._query_project_versions,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return project_versions_generator
        return list(project_versions_generator)

    def _query_project_versions(self, skip: int, first: int, payload: dict, fields: List[str]):
        payload.update({"skip": skip, "first": first})
        _gql_project_version = gql_project_version(fragment_builder(fields, ProjectVersionType))
        result = self.auth.client.execute(_gql_project_version, payload)
        return format_result("data", result)

    @typechecked
    def count_project_versions(self, project_id: str) -> int:
        """Count the number of project versions.

        Args:
            project_id: Filter on ID of project

        Returns:
            The number of project versions with the parameters provided
        """
        variables = {
            "where": {"projectId": project_id},
        }
        result = self.auth.client.execute(GQL_PROJECT_VERSION_COUNT, variables)
        count = format_result("data", result)
        return int(count)
