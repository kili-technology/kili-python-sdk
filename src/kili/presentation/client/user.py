"""Client presentation methods for users."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.enums import OrganizationRole
from kili.domain.organization import OrganizationId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.user import UserUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class UserClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on users."""

    @overload
    def users(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
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
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
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
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of users given a set of criteria.

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
            An iterable of users.

        Examples:
            ```
            # List all users in my organization
            >>> organization = kili.organizations()[0]
            >>> organization_id = organization['id']
            >>> kili.users(organization_id=organization_id)
            ```
        """
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)

        users_gen = UserUseCases(self.kili_api_gateway).list_users(
            filters=UserFilter(
                api_key=api_key,
                email=email,
                organization_id=OrganizationId(organization_id) if organization_id else None,
                activated=None,
                id=None,
                id_in=None,
            ),
            fields=fields,
            options=QueryOptions(disable_tqdm, first, skip),
        )

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
            organization_id: Identifier of the user's organization.
            api_key: Filter by API Key.
            email: Filter by email.

        Returns:
            The number of organizations with the parameters provided.
        """
        return UserUseCases(self.kili_api_gateway).count_users(
            UserFilter(
                api_key=api_key,
                email=email,
                organization_id=OrganizationId(organization_id) if organization_id else None,
                activated=None,
                id=None,
                id_in=None,
            )
        )

    @typechecked
    def create_user(
        self,
        email: str,
        password: str,
        organization_role: OrganizationRole,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
    ) -> Dict[Literal["id"], str]:
        """Add a user to your organization.

        Args:
            email: Email of the new user, used as user's unique identifier.
            password: On the first sign in, he will use this password and be able to change it.
            organization_role: One of "ADMIN", "USER".
            firstname: First name of the new user.
            lastname: Last name of the new user.

        Returns:
            A dictionary with the id of the new user.
        """
        return UserUseCases(self.kili_api_gateway).create_user(
            email=email.lower(),
            password=password,
            organization_role=organization_role,
            firstname=firstname,
            lastname=lastname,
            fields=("id",),
        )

    @typechecked
    def update_password(
        self, email: str, old_password: str, new_password_1: str, new_password_2: str
    ) -> Dict[Literal["id"], str]:
        """Allow to modify the password that you use to connect to Kili.

        This resolver only works for on-premise installations without Auth0.

        Args:
            email: Email of the person whose password has to be updated.
            old_password: The old password
            new_password_1: The new password
            new_password_2: A confirmation field for the new password

        Returns:
            A dict with the user id.
        """
        return UserUseCases(self.kili_api_gateway).update_password(
            old_password=old_password,
            new_password_1=new_password_1,
            new_password_2=new_password_2,
            user_filter=UserFilter(
                email=email,
                activated=None,
                api_key=None,
                id=None,
                id_in=None,
                organization_id=None,
            ),
            fields=("id",),
        )

    @typechecked
    def update_properties_in_user(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        organization_id: Optional[str] = None,
        organization_role: Optional[OrganizationRole] = None,
        activated: Optional[bool] = None,
    ) -> Dict[Literal["id"], str]:
        """Update the properties of a user.

        Args:
            email: The email is the identifier of the user.
            firstname: Change the first name of the user.
            lastname: Change the last name of the user.
            organization_id: Change the organization the user is related to.
            organization_role: Change the role of the user.
                One of "ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER".
            activated: In case we want to deactivate a user, but keep it.

        Returns:
            A dict with the user id.
        """
        return UserUseCases(self.kili_api_gateway).update_user(
            user_filter=UserFilter(
                email=email,
                activated=None,
                api_key=None,
                id=None,
                id_in=None,
                organization_id=None,
            ),
            firstname=firstname,
            lastname=lastname,
            organization_id=OrganizationId(organization_id) if organization_id else None,
            organization_role=organization_role,
            activated=activated,
            fields=("id",),
        )
