"""
Issue queries
"""

from dataclasses import dataclass
from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder
from .queries import GQL_ISSUES_COUNT, gql_issues
from ...types import Issue as IssueType
from ...utils import row_generator_from_paginated_calls


@dataclass
class QueriesIssue:
    """
    Set of Issue queries
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
               skip: Optional[int] = 0,
               disable_tqdm: bool = False,
               as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """
        Gets a generator or a list of issues that match a set of criteria

        Parameters
        ----------
        - fields : list of string, optional (default = ['id', 'createdAt', 'hasBeenSeen', 'status', 'type'])
            All the fields to request among the possible fields for the assets.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#issue) for all possible fields.
        - first : int, optional (default = None)
            Maximum number of issues to return.
        - project_id : str, optional (default = None)
            Project ID the issue belongs to.
        - skip : int, optional (default = None)
            Number of issues to skip (they are ordered by their date of creation, first to last).
        - disable_tqdm : bool, (default = False)
        - as_generator: bool, (default = False)
            If True, a generator on the issues is returned.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> # List all issues of a project and their authors
        >>> kili.issues(project_id=project_id, fields=['author.email'])
        """
        if as_generator is False:
            warnings.warn("From 2022-05-18, the default return type will be a generator. Currently, the default return type is a list. \n"
                          "If you want to force the query return to be a list, you can already call this method with the argument as_generator=False",
                          DeprecationWarning)

        count_args = {'project_id': project_id}
        disable_tqdm = disable_tqdm or as_generator
        payload_query = {
            'where': {
                'project': {
                    'id': project_id,
                },
            },
        }

        issues_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_issues,
            count_args,
            self._query_issues,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return issues_generator
        return list(issues_generator)

    def _query_issues(self,
                      skip: int,
                      first: int,
                      payload: dict,
                      fields: List[str]):
        payload.update({'skip': skip, 'first': first})
        _gql_issues = gql_issues(fragment_builder(fields, IssueType))
        result = self.auth.client.execute(_gql_issues, payload)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_issues(self, project_id: Optional[str] = None):
        """
        Count and return the number of api keys with the given constraints

        Parameters
        ----------
        - project_id : str, optional (default = None)
            Project ID the issue belongs to.

        Returns
        -------
        - the number of issues with the parameters provided

        """
        variables = {
            'where': {
                'project': {
                    'id': project_id,
                },
            },
        }
        result = self.auth.client.execute(GQL_ISSUES_COUNT, variables)
        count = format_result('data', result)
        return count
