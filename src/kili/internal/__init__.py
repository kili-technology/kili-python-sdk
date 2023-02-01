"""
Module for methods and classes that are for internal use by Kili Technology only.
"""

from typeguard import typechecked

from kili.helpers import format_result

from ..mutations.organization import MutationsOrganization
from ..mutations.user.queries import GQL_RESET_PASSWORD


class KiliInternal(MutationsOrganization):
    """Inherit classes for internal use by Kili Technology only."""

    def __init__(self, kili):
        """Initializes the class.

        Args:
            kili: Kili object
        """
        self.kili = kili
        super().__init__(self.kili.auth)

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
        result = self.auth.client.execute(GQL_RESET_PASSWORD, variables)
        return format_result("data", result)
