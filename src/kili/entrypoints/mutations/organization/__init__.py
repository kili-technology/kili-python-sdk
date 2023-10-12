"""Organization mutations."""

import json
from typing import Optional

from typeguard import typechecked

from kili.core.graphql.graphql_client import GraphQLClient
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call

from .queries import GQL_UPDATE_PROPERTIES_IN_ORGANIZATION


@for_all_methods(log_call, exclude=["__init__"])
class MutationsOrganization(BaseOperationEntrypointMixin):
    """Set of Organization mutations."""

    graphql_client: GraphQLClient

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
