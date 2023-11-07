"""Module for methods that are for internal use by Kili Technology only."""

from typing import Dict, Iterable, Optional

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.user.operations import get_reset_password_mutation
from kili.domain.api_key import ApiKeyFilters
from kili.domain.types import ListOrTuple
from kili.entrypoints.mutations.project.queries import GQL_DELETE_PROJECT
from kili.presentation.client.organization import InternalOrganizationClientMethods
from kili.use_cases.api_key import ApiKeyUseCases


class InternalClientMethods(InternalOrganizationClientMethods):
    """Kili client methods for internal use by Kili Technology only."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        """Initialize the class.

        Args:
            kili: Kili object
        """
        super().__init__()
        self.kili_api_gateway = kili_api_gateway

    @typechecked
    def reset_password(self, email: str):
        """Reset password.

        WARNING: This method is for internal use only.

        Args:
            email: Email of the person whose password has to be reset.

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        query = get_reset_password_mutation(fragment="id")
        variables = {"where": {"email": email}}
        result = self.kili_api_gateway.graphql_client.execute(query, variables)
        return result["data"]

    @typechecked
    def delete_project(self, project_id: str):
        """Delete project permanently.

        WARNING: This resolver is for internal use by Kili Technology only.

        Args:
            project_id: Identifier of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        variables = {"projectID": project_id}
        result = self.kili_api_gateway.graphql_client.execute(GQL_DELETE_PROJECT, variables)
        return result["data"]

    # pylint: disable=too-many-arguments
    @typechecked
    def api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = ("id", "name", "createdAt", "revoked"),
        first: Optional[int] = None,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        """Get a generator or a list of API keys that match a set of constraints.

        WARNING: This method is for internal use only.

        !!! info
            You can only query your own API keys

        Args:
            api_key_id: Identifier of the API key to retrieve.
            user_id: Identifier of the user.
            api_key: Value of the API key.
            skip: Number of assets to skip
            fields: All the fields to request among the possible fields for the assets.
            first: Maximum number of API keys to return.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the API key is returned.

        Returns:
            A result object which contains the query if it was successful,
                or an error message.
        """
        api_key_use_cases = ApiKeyUseCases(self.kili_api_gateway)
        filters = ApiKeyFilters(api_key_id=api_key_id, user_id=user_id, api_key=api_key)
        api_keys_gen = api_key_use_cases.list_api_keys(
            filters, fields, QueryOptions(first=first, skip=skip, disable_tqdm=disable_tqdm)
        )

        if as_generator:
            return api_keys_gen
        return list(api_keys_gen)

    @typechecked
    def count_api_keys(
        self,
        api_key_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> int:
        """Count and return the number of api keys with the given constraints.

        WARNING: This method is for internal use only.

        Args:
            api_key_id: Identifier of the API key to retrieve.
            user_id: Identifier of the user.
            api_key: Value of the api key.

        Returns:
            The number of API Keys matching params if it was successful,
                or an error message.
        """
        api_key_use_cases = ApiKeyUseCases(self.kili_api_gateway)
        filters = ApiKeyFilters(api_key_id=api_key_id, user_id=user_id, api_key=api_key)
        return api_key_use_cases.count_api_keys(filters)
