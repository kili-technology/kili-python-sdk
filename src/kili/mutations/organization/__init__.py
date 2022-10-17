"""Organization mutations."""

import json
from typing import Optional

from typeguard import typechecked

from ...helpers import format_result
from .queries import GQL_CREATE_ORGANIZATION, GQL_UPDATE_PROPERTIES_IN_ORGANIZATION


class MutationsOrganization:
    """Set of Organization mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initializes the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def create_organization(self, name: str, address: str, zip_code: str, city: str, country: str):
        """Create an organization.

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
        address: Optional[str] = None,
        zip_code: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        license: Optional[dict] = None,
    ):  # pylint: disable=redefined-builtin
        """Modify an organization.

        Args:
            organization_id :
            name :
            address :
            license :
            zip_code :
            city :
            country :

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        license_str = None if not license else json.dumps(license)
        variables = {"id": organization_id}
        if name is not None:
            variables["name"] = name
        if address is not None:
            variables["address"] = address
        if license_str is not None:
            variables["license"] = license_str
        if zip_code is not None:
            variables["zipCode"] = zip_code
        if city is not None:
            variables["city"] = city
        if country is not None:
            variables["country"] = country
        result = self.auth.client.execute(GQL_UPDATE_PROPERTIES_IN_ORGANIZATION, variables)
        return format_result("data", result)
