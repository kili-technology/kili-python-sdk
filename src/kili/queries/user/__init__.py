"""User queries."""

from typing import Dict, Generator, Iterable, List, Optional, overload

from typeguard import typechecked
from typing_extensions import Literal

from kili.graphql import QueryOptions
from kili.graphql.operations.user.queries import UserQuery, UserWhere
from kili.helpers import disable_tqdm_if_as_generator


class QueriesUser:
    """Set of User queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @overload
    def users(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["email", "id", "firstname", "lastname"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def users(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["email", "id", "firstname", "lastname"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def users(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["email", "id", "firstname", "lastname"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of users given a set of criteria

        Args:
            api_key: Query an user by its API Key
            email: Email of the user
            organization_id: Identifier of the user's organization
            fields: All the fields to request among the possible fields for the users.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#user) for all possible fields.
            first: Maximum number of users to return
            skip: Number of skipped users (they are ordered by creation date)
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the users is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

        Examples:
            ```
            # List all users in my organization
            >>> organization = kili.organizations()
            >>> organization_id = organizations[0]['id]
            >>> kili.users(organization_id=organization_id)
            ```
        """

        where = UserWhere(api_key=api_key, email=email, organization_id=organization_id)
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        users_gen = UserQuery(self.auth.client)(where, fields, options)

        if as_generator:
            return users_gen
        return list(users_gen)

    @typechecked
    def count_users(
        self,
        organization_id: Optional[str] = None,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
    ) -> int:
        """Get user count based on a set of constraints.

        Args:
            organization_id: Identifier of the user's organization

        Returns:
            The number of organizations with the parameters provided
        """
        where = UserWhere(api_key=api_key, email=email, organization_id=organization_id)
        return UserQuery(self.auth.client).count(where)
