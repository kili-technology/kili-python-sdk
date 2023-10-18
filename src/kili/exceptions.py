"""Exceptions of the package."""

from typing import Dict, List, Optional


class GraphQLError(Exception):
    """Raised when the GraphQL call returns an error."""

    def __init__(self, error, batch_number=None) -> None:
        self.error = error

        if isinstance(error, List):
            error = error[0]
        if isinstance(error, Dict) and "message" in error:
            error_msg = error["message"]
        else:
            error_msg = str(error)

        if batch_number is None:
            super().__init__(f'GraphQL error: "{error_msg}"')
        else:
            super().__init__(f'GraphQL error at index {100*batch_number}: {error_msg}"')


class NotFound(Exception):
    """Used when a given object is not found in Kili."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def __str__(self) -> str:
        return f"Not found: '{self.name}'"


class AuthenticationFailed(Exception):
    """Used when the authentification fails."""

    def __init__(self, api_key, api_endpoint, error_msg: Optional[str] = None) -> None:
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

    @staticmethod
    def _obfuscate(input_str: str) -> str:
        if len(input_str) >= 4:
            return "*" * (len(input_str) - 4) + input_str[-4:]
        return input_str


class MissingArgumentError(ValueError):
    """Raised when an required argument was not given by the user."""


class IncompatibleArgumentsError(ValueError):
    """Raised when the user gave at least two incompatible arguments."""
