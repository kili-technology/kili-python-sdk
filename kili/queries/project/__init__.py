from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_projects, GQL_PROJECTS_COUNT
from ...types import Project
from ...constants import NO_ACCESS_RIGHT


class QueriesProject:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def projects(self,
                 project_id: str = None,
                 search_query: str = None,
                 should_relaunch_kpi_computation: bool = None,
                 updated_at_gte: str = None,
                 updated_at_lte: str = None,
                 skip: int = 0,
                 fields: list = ['consensusTotCoverage', 'id', 'inputType', 'interfaceCategory', 'jsonInterface',
                                 'maxWorkerCount', 'minAgreement', 'minConsensusSize', 'roles.id', 'roles.role',
                                 'roles.user.email', 'roles.user.id', 'roles.user.name', 'title'],
                 first: int = 100):
        """
        Get projects with a search_query

        Parameters
        ----------
        - project_id : str, optional (default = None)
            Select a specific project through its project_id
        - search_query : str, optional (default = None)
            Returned projects have a title or a description that matches this string.
        - should_relaunch_kpi_computation : bool, optional (default = None)
            Technical field, added to indicate changes in honeypot or consensus settings
        - updated_at_gte : string, optional (default = None)
            Returned projects should have a label whose update date is greated or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned projects should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - skip : int, optional (default = 0)
            Number of projects to skip (they are ordered by their creation)
        - fields : list of string, optional (default = ['consensusTotCoverage', 'id', 'inputType', 'interfaceCategory', 'jsonInterface', 'maxWorkerCount', 'minAgreement', 'minConsensusSize', 'roles.id', 'roles.role', 'roles.user.email', 'roles.user.id', 'roles.user.name', 'title'])
            All the fields to request among the possible fields for the projects, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#project
        - first : int , optional (default = 100)
            Maximum number of projects to return. Can only be between 0 and 100.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        GQL_PROJECTS = gql_projects(fragment_builder(fields, Project))
        variables = {
            'where': {
                'id': project_id,
                'searchQuery': search_query,
                'shouldRelaunchKpiComputation': should_relaunch_kpi_computation,
                'updatedAtGte': updated_at_gte,
                'updatedAtLte': updated_at_lte,
            },
            'skip': skip,
            'first': first
        }
        result = self.auth.client.execute(GQL_PROJECTS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def count_projects(self, project_id: str = None, search_query: str = None, should_relaunch_kpi_computation: bool = None, updated_at_gte: str = None, updated_at_lte: str = None):
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
            Returned projects should have a label whose update date is greated or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned projects should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"

        Returns
        -------
        - a positive integer corresponding to the number of results of the query if it was successful, or an error message else.
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
