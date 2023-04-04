"""Project version queries."""

from typing import Dict, Generator, Iterable, List, Optional, overload

from typeguard import typechecked
from typing_extensions import Literal

from kili.core.authentication import KiliAuth
from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.project_version.queries import (
    ProjectVersionQuery,
    ProjectVersionWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesProjectVersion:
    """Set of ProjectVersion queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @overload
    def project_version(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: List[str] = ["createdAt", "id", "content", "name", "projectId"],
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def project_version(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: List[str] = ["createdAt", "id", "content", "name", "projectId"],
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def project_version(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: List[str] = ["createdAt", "id", "content", "name", "projectId"],
        disable_tqdm: bool = False,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of project versions respecting a set of criteria.

        Args:
            project_id: Filter on Id of project
            fields: All the fields to request among the possible fields for the project versions
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#projectVersions) for all possible fields.
            first: Number of project versions to query
            skip: Number of project versions to skip (they are ordered by their date
                of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project versions is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """
        where = ProjectVersionWhere(
            project_id=project_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        project_versions_gen = ProjectVersionQuery(self.auth.client)(where, fields, options)

        if as_generator:
            return project_versions_gen
        return list(project_versions_gen)

    @typechecked
    def count_project_versions(self, project_id: str) -> int:
        """Count the number of project versions.

        Args:
            project_id: Filter on ID of project

        Returns:
            The number of project versions with the parameters provided
        """
        where = ProjectVersionWhere(
            project_id=project_id,
        )
        return ProjectVersionQuery(self.auth.client).count(where)
