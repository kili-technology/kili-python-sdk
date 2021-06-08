from typing import List, Optional

from typeguard import typechecked

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_issues
from ...types import Issue as IssueType


class QueriesIssue:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    @typechecked
    def issues(self,
               fields: Optional[list] = [
                       'id',
                       'createdAt',
                       'hasBeenSeen',
                       'issueNumber',
                       'status',
                       'type'],
               first: Optional[int] = 100,
               project_id: Optional[str] = None,
               skip: Optional[int] = 0):
        """
        Get an array of issues given a set of criteria

        Parameters
        ----------
        - project_id : str, optional (default = None)
            Project ID the issue belongs to.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # List all issues of a project and their authors
        >>> kili.issues(project_id=project_id, fields=['author.email'])
        """
        variables = {
            'where': {
                'project': {
                    'id': project_id,
                },
            },
            'skip': skip,
            'first': first,
        }
        GQL_ISSUES = gql_issues(fragment_builder(fields, IssueType))
        result = self.auth.client.execute(GQL_ISSUES, variables)
        return format_result('data', result)
