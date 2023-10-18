"""User use cases."""

from typing import Dict, Generator, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.user.types import (
    CreateUserDataKiliGatewayInput,
    UserDataKiliGatewayInput,
)
from kili.core.enums import OrganizationRole
from kili.domain.organization import OrganizationId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter
from kili.use_cases.base import BaseUseCases


class UserUseCases(BaseUseCases):
    """User use cases."""

    def list_users(
        self, filters: UserFilter, fields: ListOrTuple[str], options: QueryOptions
    ) -> Generator[Dict, None, None]:
        """List all users."""
        return self._kili_api_gateway.list_users(
            fields=fields, user_filters=filters, options=options
        )

    def count_users(self, filters: UserFilter) -> int:
        """Count users."""
        return self._kili_api_gateway.count_users(user_filters=filters)

    def create_user(
        self,
        email: str,
        password: str,
        organization_role: OrganizationRole,
        firstname: Optional[str],
        lastname: Optional[str],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Create a user."""
        return self._kili_api_gateway.create_user(
            data=CreateUserDataKiliGatewayInput(
                email=email,
                password=password,
                organization_role=organization_role,
                firstname=firstname,
                lastname=lastname,
            ),
            fields=fields,
        )

    def update_password(
        self,
        old_password: str,
        new_password_1: str,
        new_password_2: str,
        user_filter: UserFilter,
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update user password."""
        return self._kili_api_gateway.update_password(
            old_password=old_password,
            new_password_1=new_password_1,
            new_password_2=new_password_2,
            user_filter=user_filter,
            fields=fields,
        )

    def update_user(
        self,
        user_filter: UserFilter,
        firstname: Optional[str],
        lastname: Optional[str],
        organization_id: Optional[OrganizationId],
        organization_role: Optional[OrganizationRole],
        activated: Optional[bool],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Update user."""
        return self._kili_api_gateway.update_user(
            user_filter=user_filter,
            data=UserDataKiliGatewayInput(
                activated=activated,
                firstname=firstname,
                lastname=lastname,
                organization_id=organization_id,
                organization_role=organization_role,
                api_key=None,
                email=None,
                has_completed_labeling_tour=None,
                hubspot_subscription_status=None,
                organization=None,
            ),
            fields=fields,
        )
