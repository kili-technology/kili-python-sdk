"""Exceptions of the package."""

from typing import Optional

from kili.core.simplified_errors import (
    is_error_simplification_enabled,
    simplify_graphql_error_message,
)


class GraphQLError(Exception):
    """Raised when the GraphQL call returns an error."""

    def __init__(self, error, batch_number=None, context=None) -> None:
        self.error = error
        self.context = context

        if isinstance(error, list):
            error = error[0]
        if isinstance(error, dict) and "message" in error:
            error_msg = error["message"]
        else:
            error_msg = str(error)

        if is_error_simplification_enabled():
            error_msg = simplify_graphql_error_message(error_msg)
            if batch_number is not None:
                error_msg = f"{error_msg} (at index {100*batch_number})"
            super().__init__(error_msg)
        elif batch_number is None:
            super().__init__(f'GraphQL error: "{error_msg}"')
        else:
            super().__init__(f'GraphQL error at index {100*batch_number}: "{error_msg}"')


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
        if is_error_simplification_enabled():
            super().__init__(self._simplified_message(api_key, api_endpoint, error_msg))
        elif api_key is None:
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

    @classmethod
    def _simplified_message(
        cls, api_key: Optional[str], api_endpoint: str, error_msg: Optional[str]
    ) -> str:
        if not api_key:
            return (
                "No API key provided."
                " Set the `KILI_API_KEY` environment variable or pass `api_key` to the client."
            )
        if error_msg and "api key" in error_msg.lower():
            return f"Invalid API key `{cls._obfuscate(api_key)}`"
        message = f"Connection to Kili endpoint {api_endpoint} failed"
        message += f" with API key `{cls._obfuscate(api_key)}`"
        if error_msg:
            message += f": {error_msg}"
        return message

    @staticmethod
    def _obfuscate(input_str: str) -> str:
        if len(input_str) >= 4:
            return "*" * (len(input_str) - 4) + input_str[-4:]
        return input_str


class MissingArgumentError(ValueError):
    """Raised when an required argument was not given by the user."""


class IncompatibleArgumentsError(ValueError):
    """Raised when the user gave at least two incompatible arguments."""
