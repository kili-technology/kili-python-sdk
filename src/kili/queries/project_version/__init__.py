"""Project version queries."""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.project_version.queries import (
    ProjectVersionQuery,
    ProjectVersionWhere,
)


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
    ) -> Iterable[Dict]:
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
        where = ProjectVersionWhere(
            project_id=project_id,
        )
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return ProjectVersionQuery(self.auth.client)(where, fields, options)

    @typechecked
    def count_project_versions(self, project_id: str) -> int:
        """Count the number of project versions.

        Args:
            project_id: Filter on ID of project

        Returns:
            The number of project versions with the parameters provided
        """
        where = ProjectVersionWhere(
            project_id=project_id,
        )
        return ProjectVersionQuery(self.auth.client).count(where)
