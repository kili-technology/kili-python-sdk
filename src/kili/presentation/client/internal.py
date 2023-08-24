"""Module for methods that are for internal use by Kili Technology only."""

from typeguard import typechecked

from kili.entrypoints.mutations.organization import MutationsOrganization
from kili.entrypoints.mutations.project.queries import GQL_DELETE_PROJECT
from kili.entrypoints.mutations.user.queries import GQL_RESET_PASSWORD
from kili.entrypoints.queries.api_key import QueriesApiKey


class InternalClientMethods(MutationsOrganization, QueriesApiKey):
    """Kili client methods for internal use by Kili Technology only."""

    def __init__(self, kili):
        """Initializes the class.

        Args:
            kili: Kili object
        """
        super().__init__()
        self.kili = kili

        self.graphql_client = kili.graphql_client
        self.http_client = kili.http_client
        self.format_result = kili.format_result

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
        variables = {"where": {"email": email}}
        result = self.graphql_client.execute(GQL_RESET_PASSWORD, variables)
        return self.format_result("data", result)

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
        result = self.graphql_client.execute(GQL_DELETE_PROJECT, variables)
        return self.format_result("data", result)
