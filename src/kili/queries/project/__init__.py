"""Project queries."""

from typing import Dict, Generator, List, Optional, Union

from typeguard import typechecked

from kili.helpers import format_result, fragment_builder
from kili.queries.project.queries import GQL_PROJECTS_COUNT, gql_projects
from kili.types import Project
from kili.utils.pagination import row_generator_from_paginated_calls


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
    ) -> Union[List[Dict], Generator]:
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

        saved_args = locals()
        count_args = {
            k: v
            for (k, v) in saved_args.items()
            if k
            in [
                "project_id",
                "search_query",
                "should_relaunch_kpi_computation",
                "updated_at_gte",
                "updated_at_lte",
            ]
        }
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            "where": {
                "id": project_id,
                "searchQuery": search_query,
                "shouldRelaunchKpiComputation": should_relaunch_kpi_computation,
                "updatedAtGte": updated_at_gte,
                "updatedAtLte": updated_at_lte,
            },
        }

        projects_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_projects,
            count_args,
            self._query_projects,
            payload_query,
            fields,
            disable_tqdm,
        )

        if as_generator:
            return projects_generator
        return list(projects_generator)

    def _query_projects(self, skip: int, first: int, payload: dict, fields: List[str]):
        payload.update({"skip": skip, "first": first})
        _gql_projects = gql_projects(fragment_builder(fields, Project))
        result = self.auth.client.execute(_gql_projects, payload)
        return format_result("data", result)

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
        variables = {
            "where": {
                "id": project_id,
                "searchQuery": search_query,
                "shouldRelaunchKpiComputation": should_relaunch_kpi_computation,
                "updatedAtGte": updated_at_gte,
                "updatedAtLte": updated_at_lte,
            }
        }
        result = self.auth.client.execute(GQL_PROJECTS_COUNT, variables)
        return format_result("data", result, int)
