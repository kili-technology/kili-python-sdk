"""Project user queries."""

from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    overload,
)

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)
from kili.domain.types import ListOrTuple
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesProjectUser(BaseOperationEntrypointMixin):
    """Set of ProjectUser queries."""

    # pylint: disable=too-many-arguments,redefined-builtin

    @overload
    def project_users(
        self,
        project_id: str,
        email: Optional[str] = None,
        id: Optional[str] = None,
        organization_id: Optional[str] = None,
        status_in: Optional[Sequence[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]]] = (
            "ACTIVATED",
            "ORG_ADMIN",
        ),
        fields: ListOrTuple[str] = (
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
            "status",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
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
        status_in: Optional[Sequence[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]]] = (
            "ACTIVATED",
            "ORG_ADMIN",
        ),
        fields: ListOrTuple[str] = (
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
            "status",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
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
        status_in: Optional[Sequence[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]]] = (
            "ACTIVATED",
            "ORG_ADMIN",
        ),
        fields: ListOrTuple[str] = (
            "activated",
            "id",
            "role",
            "starred",
            "user.email",
            "user.id",
            "status",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Return project users (possibly with their KPIs) that match a set of criteria.

        Args:
            project_id: Identifier of the project.
            email: Email of the user.
            id: Identifier of the user.
            organization_id: Identifier of the user's organization.
            status_in: If `None`, all users are returned.

                - `ORG_ADMIN`: Is an Organization Admin. Is automatically added to projects.
                - `ACTIVATED`: Has been invited to the project. Is not an Organization Admin
                - `ORG_SUSPENDED`: Has been suspended at the organization level. Can no longer access any projects.
            fields: All the fields to request among the possible fields for the projectUsers.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#projectuser) for all possible fields.
            first: Maximum number of users to return.
            skip: Number of project users to skip.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the project users is returned.

        Returns:
            An iterable with the project users that match the criteria.

        Examples:
            ```python
            # Retrieve consensus marks of all users in project
            >>> kili.project_users(project_id=project_id, fields=['consensusMark', 'user.email'])
            ```
        """
        if status_in is not None and "status" not in fields:
            fields = [*fields, "status"]

        where = ProjectUserWhere(
            project_id=project_id,
            email=email,
            _id=id,
            organization_id=organization_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        project_users_gen = ProjectUserQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if status_in is not None:
            status_in_set = set(status_in)
            project_users_gen = (
                project_user
                for project_user in project_users_gen
                if project_user["status"] in status_in_set
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
        status_in: Optional[Sequence[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]]] = (
            "ACTIVATED",
            "ORG_ADMIN",
        ),
    ) -> int:
        # pylint: disable=line-too-long
        """Count the number of projects and their users that match a set of criteria.

        Args:
            project_id: Identifier of the project
            email: Email of the user
            id: Identifier of the user
            organization_id: Identifier of the user's organization
            status_in: If `None`, all users are returned.

                - `ORG_ADMIN`: Is an Organization Admin. Is automatically added to projects.
                - `ACTIVATED`: Has been invited to the project. Is not an Organization Admin
                - `ORG_SUSPENDED`: Has been suspended at the organization level. Can no longer access any projects.

        Returns:
            The number of project users with the parameters provided
        """
        if status_in is None:
            where = ProjectUserWhere(
                project_id=project_id,
                email=email,
                _id=id,
                organization_id=organization_id,
            )
            return ProjectUserQuery(self.graphql_client, self.http_client).count(where)

        count = 0
        for status in set(status_in):
            where = ProjectUserWhere(
                project_id=project_id,
                email=email,
                _id=id,
                organization_id=organization_id,
                status=status,
            )
            count += ProjectUserQuery(self.graphql_client, self.http_client).count(where)
        return count
