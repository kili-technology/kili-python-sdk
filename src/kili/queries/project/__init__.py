"""Project queries."""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked

from kili.graphql import QueryOptions
from kili.graphql.operations.project.queries import ProjectQuery, ProjectWhere


class QueriesProject:
    """Set of Project queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @typechecked
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        skip: int = 0,
        fields: List[str] = [
            "consensusTotCoverage",
            "id",
            "inputType",
            "jsonInterface",
            "minConsensusSize",
            "reviewCoverage",
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
            "title",
        ],
        first: Optional[int] = None,
        disable_tqdm: bool = False,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of projects that match a set of criteria.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation : Technical field, added to indicate changes in honeypot or consensus settings.
            updated_at_gte: Returned projects should have a label whose update date is greater or equal
                to this date.
            updated_at_lte: Returned projects should have a label whose update date is lower or equal to this date.
            skip: Number of projects to skip (they are ordered by their creation).
            fields: All the fields to request among the possible fields for the projects.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#project) for all possible fields.
            first: Maximum number of projects to return.
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the projects is returned.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            >>> # List all my projects
            >>> kili.projects()
        """

        where = ProjectWhere(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
        )
        options = QueryOptions(disable_tqdm, first, skip, as_generator)
        return ProjectQuery(self.auth.client)(where, fields, options)

    @typechecked
    def count_projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
    ) -> int:
        # pylint: disable=line-too-long
        """
        Counts the number of projects with a search_query

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation : Technical field, added to indicate changes in honeypot
                or consensus settings
            updated_at_gte: Returned projects should have a label
                whose update date is greater
                or equal to this date.
            updated_at_lte: Returned projects should have a label
                whose update date is lower or equal to this date.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            The number of projects with the parameters provided
        """
        where = ProjectWhere(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
        )
        return ProjectQuery(self.auth.client).count(where)
