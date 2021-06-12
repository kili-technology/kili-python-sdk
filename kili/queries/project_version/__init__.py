from typing import List, Optional

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_project_version, GQL_PROJECT_VERSION_COUNT
from ...types import ProjectVersion as ProjectVersionType

class QueriesProjectVersion:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v2'])
    @typechecked
    def project_version(self,
                      first: Optional[int] = 100,
                      skip: Optional[int] = 0,
                      fields: List[str] = ['createdAt', 'id', 'content', 'name', 'project', 'projectId'],
                      project_id: str = None,
                      ):
        """
        Get an array of project version given a set of constraints

        Parameters
        ----------
        - fields : list of string, optional (default = ['createdAt', 'id', 'content', 'name', 'project'])
            All the fields to request among the possible fields for the project versions
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectVersions) for all possible fields.
        - first : int (default = 100)
            Optional, Number of project versions to query
        - project_id : string (default = '')
            Filter on Id of project
        - skip : int (default = 0)
            Optional, number of project versions to skip (they are ordered by their date of creation, first to last).

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        formatted_first = first if first else 100
        variables = {
            'where': {
                'projectId': project_id,
            },
            'skip': skip,
            'first': formatted_first,
        }
        GQL_PROJECT_VERSION = gql_project_version(
            fragment_builder(fields, ProjectVersionType))
        result = self.auth.client.execute(GQL_PROJECT_VERSION, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_project_versions(self,
                            project_id: str):
        """
        Count the number of project versions

        Parameters
        ----------
        - project_id :
            Filter on ID of project

        Returns
        -------
        - the number of project versions with the parameters provided
        """
        variables = {
            'where': { 'projectId' : project_id
            },
        }
        result = self.auth.client.execute(GQL_PROJECT_VERSION_COUNT, variables)
        count = format_result('data', result)
        return count
