"""Project version queries."""

from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked


from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_project_version, GQL_PROJECT_VERSION_COUNT
from ...types import ProjectVersion as ProjectVersionType
from ...utils import row_generator_from_paginated_calls


class QueriesProjectVersion:
    """Set of ProjectVersion queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v2'])
    @typechecked
    def project_version(
            self,
            first: Optional[int] = 100,
            skip: Optional[int] = 0,
            fields: List[str] = [
                'createdAt',
                'id',
                'content',
                'name',
                'project',
                'projectId'],
            project_id: str = None,
            disable_tqdm: bool = False,
            as_generator: bool = False) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a generator or a list of project versions respecting a set of criteria.

        Args:
            fields: All the fields to request among the possible fields for the project versions
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#projectVersions) for all possible fields.
            first: Number of project versions to query
            project_id: Filter on Id of project
            skip: Number of project versions to skip (they are ordered by their date
                of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project versions is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """

        count_args = {"project_id": project_id}
        disable_tqdm = disable_tqdm or as_generator
        payload_query = {
            'where': {
                'projectId': project_id,
            },
        }
        project_versions_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_project_versions,
            count_args,
            self._query_project_versions,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return project_versions_generator
        return list(project_versions_generator)

    def _query_project_versions(self,
                                skip: int,
                                first: int,
                                payload: dict,
                                fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_project_version = gql_project_version(
            fragment_builder(fields, ProjectVersionType))
        result = self.auth.client.execute(_gql_project_version, payload)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def count_project_versions(self, project_id: str) -> int:
        """Count the number of project versions.

        Args:
            project_id: Filter on ID of project

        Returns:
            The number of project versions with the parameters provided
        """
        variables = {
            'where': {'projectId': project_id},
        }
        result = self.auth.client.execute(GQL_PROJECT_VERSION_COUNT, variables)
        count = format_result('data', result)
        return count
