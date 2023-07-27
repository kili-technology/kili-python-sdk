"""Organization mutations."""

import json
from typing import Optional

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call

from .queries import GQL_CREATE_ORGANIZATION, GQL_UPDATE_PROPERTIES_IN_ORGANIZATION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsOrganization(BaseOperationEntrypointMixin):
    """Set of Organization mutations."""

    graphql_client: GraphQLClient

    # pylint: disable=too-many-arguments
    @typechecked
    def create_organization(self, name: str, address: str, zip_code: str, city: str, country: str):
        """Create an organization.

        WARNING: This method is for internal use only.

        Each user must be linked to an organization

        Args:
            name : Name of the organization
            address : Address of the organization
            zip_code : Zip code of the organization
            city : City of the organization
            country : Country of the organization

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
        result = self.graphql_client.execute(GQL_CREATE_ORGANIZATION, variables)
        return self.format_result("data", result)

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
        result = self.graphql_client.execute(GQL_UPDATE_PROPERTIES_IN_ORGANIZATION, variables)
        return self.format_result("data", result)
