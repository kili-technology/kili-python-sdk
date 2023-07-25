"""Project user queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesProjectUser(BaseOperationEntrypointMixin):
    """Set of ProjectUser queries."""

    # pylint: disable=too-many-arguments,redefined-builtin,dangerous-default-value,invalid-name

    @overload
    def project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = [
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = [
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = [
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Return project users (possibly with their KPIs) that match a set of criteria.

        Args:
            project_id: Identifier of the project
            email: Email of the user
            id: Identifier of the user
            organization_id: Identifier of the user's organization
            fields: All the fields to request among the possible fields for the projectUsers
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#projectuser) for all possible fields.
            first: Maximum number of users to return
            skip: Number of project users to skip
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project users is returned.

        Returns:
            An iterable with the project users that match the criteria.

        Examples:
            ```
            # Retrieve consensus marks of all users in project
            >>> kili.project_users(project_id=project_id, fields=['consensusMark', 'user.email'])
            ```
        """
        where = ProjectUserWhere(
            project_id=project_id, email=email, _id=id, organization_id=organization_id
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        project_users_gen = ProjectUserQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if as_generator:
            return project_users_gen
        return list(project_users_gen)

    @typechecked
    def count_project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> int:
        """Counts the number of projects and their users that match a set of criteria.

        Args:
            email: Email of the user
            id: Identifier of the user
            organization_id: Identifier of the user's organization
            project_id: Identifier of the project

        Returns:
            The number of project users with the parameters provided
        """
        where = ProjectUserWhere(
            project_id=project_id, email=email, _id=id, organization_id=organization_id
        )
        return ProjectUserQuery(self.graphql_client, self.http_client).count(where)
