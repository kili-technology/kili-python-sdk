"""Issue queries."""

from dataclasses import dataclass
from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked

from ...helpers import Compatible, format_result, fragment_builder, deprecate
from .queries import GQL_ISSUES_COUNT, gql_issues
from ...types import Issue as IssueType
from ...utils.pagination import row_generator_from_paginated_calls


@dataclass
class QueriesIssue:
    """Set of Issue queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    @deprecate(removed_in="2.116")
    def issues(self,
               fields: Optional[List[str]] = [
                   'id',
                   'createdAt',
                   'hasBeenSeen',
                   'issueNumber',
                   'status',
                   'type'],
               first: Optional[int] = None,
               project_id: Optional[str] = None,
               skip: Optional[int] = 0,
               disable_tqdm: bool = False,
               as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of issues that match a set of criteria.

        Args:
            fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#issue) for all possible fields.
            first: Maximum number of issues to return.
            project_id: Project ID the issue belongs to.
            skip: Number of issues to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the issues is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            >>> kili.issues(project_id=project_id, fields=['author.email']) # List all issues of a project and their authors
        """
        if project_id is None:
            message = """
                The field `project_id` must be specified since: 2.115
                It will be made mandatory in: 2.116
                If your workflow involves getting these entities over several projects,
                please iterate on your projects with .projects and concatenate the results.
                """
            warnings.warn(message, DeprecationWarning)

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
    @deprecate(removed_in="2.116")
    def count_issues(self, project_id: Optional[str] = None) -> int:
        """Count and return the number of api keys with the given constraints.

        Args:
            project_id: Project ID the issue belongs to.

        Returns:
            The number of issues with the parameters provided

        """
        if project_id is None:
            message = """
                The field `project_id` must be specified since: 2.115
                It will be made mandatory in: 2.116
                If your workflow involves getting these entities over several projects,
                please iterate on your projects with .projects and concatenate the results.
                """
            warnings.warn(message, DeprecationWarning)
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
