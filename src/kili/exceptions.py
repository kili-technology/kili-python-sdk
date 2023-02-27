"""Exceptions of the package."""
from typing import Optional


class GraphQLError(Exception):
    """Raised when the GraphQL call returns an error"""


class NotFound(Exception):
    """Used when a given object is not found in Kili"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"Not found: '{self.name}'"


class AuthenticationFailed(Exception):
    """
    Used when the authentification fails
    """

    @staticmethod
    def _obfuscate(input_str: str) -> str:
        if len(input_str) >= 4:
            return "*" * (len(input_str) - 4) + input_str[-4:]
        return input_str

    def __init__(self, api_key, api_endpoint, error_msg: Optional[str] = None):
        if api_key is None:
            super().__init__(
                "You need to provide an API KEY to connect."
                " Visit https://docs.kili-technology.com/reference/creating-an-api-key"
            )
        else:
            raise_msg = (
                f"Connection to Kili endpoint {api_endpoint} failed with API key:"
                f" {self._obfuscate(api_key)}. Check your connection and API key."
            )
            if error_msg is not None:
                raise_msg += f"\nError message:\n{error_msg}"
            super().__init__(raise_msg)


class NonExistingFieldError(ValueError):
    """Raised when querying a field that does not exist on an object"""


class MissingArgumentError(ValueError):
    """Raised when an required argument was not given by the user"""


class IncompatibleArgumentsError(ValueError):
    """Raised when the user gave at least two incompatible arguments"""


class RemovedMethodError(Exception):
    """Raised when the method used has been removed from SDK"""


class UserNotFoundError(Exception):
    """Raised when the user is not found"""
