"""Project queries."""

from typing import Optional

from typeguard import typechecked

from kili.core.graphql.operations.project.queries import ProjectQuery, ProjectWhere
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesProject(BaseOperationEntrypointMixin):
    """Set of Project queries."""

    # pylint: disable=too-many-arguments

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
        """Count the number of projects with a search_query.

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
