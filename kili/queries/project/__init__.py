"""
Project queries
"""

from typing import Generator, List, Optional, Union
import warnings
from typeguard import typechecked


from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_projects, GQL_PROJECTS_COUNT
from ...types import Project
from ...constants import NO_ACCESS_RIGHT
from ...utils import row_generator_from_paginated_calls


class QueriesProject:
    """
    Set of Project queries
    """
    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    def projects(self,
                 project_id: Optional[str] = None,
                 search_query: Optional[str] = None,
                 should_relaunch_kpi_computation: Optional[bool] = None,
                 updated_at_gte: Optional[str] = None,
                 updated_at_lte: Optional[str] = None,
                 skip: int = 0,
                 fields: list = [
                     'consensusTotCoverage',
                     'id',
                     'inputType',
                     'interfaceCategory',
                     'jsonInterface',
                     'minConsensusSize',
                     'reviewCoverage',
                     'roles.id',
                     'roles.role',
                     'roles.user.email',
                     'roles.user.id',
                     'title'],
                 first: int = 100,
                 disable_tqdm: bool = False,
                 as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Get a generator or a list of projects that match a set of criteria

        Parameters
        ----------
        - project_id : str, optional (default = None)
            Select a specific project through its project_id.
        - search_query : str, optional (default = None)
            Returned projects with a title or a description matching this string.
        - should_relaunch_kpi_computation : bool, optional (default = None)
            Technical field, added to indicate changes in honeypot or consensus settings.
        - updated_at_gte : string, optional (default = None)
            Returned projects should have a label whose update date is greater or equal
            to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned projects should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - skip : int, optional (default = 0)
            Number of projects to skip (they are ordered by their creation).
        - fields : list of string, optional (default = ['consensusTotCoverage', 'id',
            'inputType', 'interfaceCategory', 'jsonInterface', 'minConsensusSize', 'roles.id', 'roles.role',
            'roles.user.email', 'roles.user.id', 'title'])
            All the fields to request among the possible fields for the projects.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#project) for all possible fields.
        - first : int , optional (default = 100)
            Maximum number of projects to return.
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the projects is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # List all my projects
        >>> kili.projects()
        """

        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        saved_args = locals()
        count_args = {
            k: v
            for (k, v) in saved_args.items() if k in [
                'project_id',
                'search_query',
                'should_relaunch_kpi_computation',
                'updated_at_gte',
                'updated_at_lte'
            ]
        }
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            'where': {
                'id': project_id,
                'searchQuery': search_query,
                'shouldRelaunchKpiComputation': should_relaunch_kpi_computation,
                'updatedAtGte': updated_at_gte,
                'updatedAtLte': updated_at_lte,
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
            disable_tqdm
        )

        if as_generator:
            return projects_generator
        return list(projects_generator)

    def _query_projects(self,
                        skip: int,
                        first: int,
                        payload: dict,
                        fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_projects = gql_projects(fragment_builder(fields, Project))
        result = self.auth.client.execute(_gql_projects, payload)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_projects(
            self,
            project_id: Optional[str] = None,
            search_query: Optional[str] = None,
            should_relaunch_kpi_computation: Optional[bool] = None,
            updated_at_gte: Optional[str] = None,
            updated_at_lte: Optional[str] = None):
        """
        Counts the number of projects with a search_query

        Parameters
        ----------
        - project_id : str, optional (default = None)
            Select a specific project through its project_id
        - search_query : str, optional (default = None)
            Returned projects have a title or a description that matches this string.
        - should_relaunch_kpi_computation : bool, optional (default = None)
            Technical field, added to indicate changes in honeypot or consensus settings
        - updated_at_gte : string, optional (default = None)
            Returned projects should have a label whose update date is greater
            or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned projects should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"

        Returns
        -------
        - a positive integer corresponding to the number of results of the query
            if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'id': project_id,
                'searchQuery': search_query,
                'shouldRelaunchKpiComputation': should_relaunch_kpi_computation,
                'updatedAtGte': updated_at_gte,
                'updatedAtLte': updated_at_lte,
            }
        }
        result = self.auth.client.execute(GQL_PROJECTS_COUNT, variables)
        count = format_result('data', result)
        return count
