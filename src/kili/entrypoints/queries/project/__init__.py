"""Project queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.project.queries import ProjectQuery, ProjectWhere
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesProject(BaseOperationEntrypointMixin):
    """Set of Project queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
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
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
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
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
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
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of projects that match a set of criteria.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation: Technical field, added to indicate changes in honeypot or consensus settings.
            updated_at_gte: Returned projects should have a label whose update date is greater or equal
                to this date.
            updated_at_lte: Returned projects should have a label whose update date is lower or equal to this date.
            archived: If `True`, only archived projects are returned, if `False`, only active projects are returned.
                `None` disables this filter.
            skip: Number of projects to skip (they are ordered by their creation).
            fields: All the fields to request among the possible fields for the projects.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#project) for all possible fields.
            first: Maximum number of projects to return.
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the projects is returned.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A list of projects or a generator of projects if `as_generator` is `True`.

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
            archived=archived,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        projects_gen = ProjectQuery(self.graphql_client, self.http_client)(where, fields, options)

        if as_generator:
            return projects_gen
        return list(projects_gen)

    @typechecked
    def count_projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> int:
        # pylint: disable=line-too-long
        """Counts the number of projects with a search_query.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation: Technical field, added to indicate changes in honeypot
                or consensus settings
            updated_at_gte: Returned projects should have a label
                whose update date is greater
                or equal to this date.
            updated_at_lte: Returned projects should have a label
                whose update date is lower or equal to this date.
            archived: If `True`, only archived projects are returned, if `False`, only active projects are returned.
                None disable this filter.

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
            archived=archived,
        )
        return ProjectQuery(self.graphql_client, self.http_client).count(where)
