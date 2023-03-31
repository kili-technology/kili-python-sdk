"""Organization mutations."""

import json
from typing import Optional

from typeguard import typechecked

from kili.core.authentication import KiliAuth
from kili.core.helpers import format_result
from kili.utils.logcontext import for_all_methods, log_call

from .queries import GQL_CREATE_ORGANIZATION, GQL_UPDATE_PROPERTIES_IN_ORGANIZATION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsOrganization:
    """Set of Organization mutations."""

    # pylint: disable=too-many-arguments

    def __init__(self, auth: KiliAuth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def create_organization(self, name: str, address: str, zip_code: str, city: str, country: str):
        """Create an organization.
        WARNING: This method is for internal use only.

        Each user must be linked to an organization

        Args:
            name :
            address :
            zip_code :
            city :
            country :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {
            "data": {
                "name": name,
                "address": address,
                "zipCode": zip_code,
                "city": city,
                "country": country,
            }
        }
        result = self.auth.client.execute(GQL_CREATE_ORGANIZATION, variables)
        return format_result("data", result)

    @typechecked
    def update_properties_in_organization(
        self,
        organization_id: str,
        name: Optional[str] = None,
        license: Optional[dict] = None,
    ):  # pylint: disable=redefined-builtin
        """Modify an organization.
        WARNING: This method is for internal use only.

        Args:
            organization_id :
            name :
            license :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        license_str = None if not license else json.dumps(license)
        variables = {"id": organization_id}
        if name is not None:
            variables["name"] = name
        if license_str is not None:
            variables["license"] = license_str
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_ORGANIZATION, variables)
        return format_result("data", result)
