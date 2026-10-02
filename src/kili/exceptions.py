"""Exceptions of the package."""

from typing import Optional

from requests.exceptions import ConnectionError as RequestsConnectionError


class GraphQLError(Exception):
    """Raised when the GraphQL call returns an error."""

    def __init__(self, error, batch_number=None, context=None, index=None) -> None:
        self.error = error
        self.context = context

        if isinstance(error, list):
            error = error[0]
        if isinstance(error, dict) and "message" in error:
            error_msg = error["message"]
        else:
            error_msg = str(error)

        if index is None and batch_number is not None:
            index = 100 * batch_number
        if index is None:
            super().__init__(f'GraphQL error: "{error_msg}"')
        else:
            super().__init__(f'GraphQL error at index {index}: "{error_msg}"')


class MutationOutcomeUnknownError(RequestsConnectionError):
    """Raised when a mutation failed in a way that does not tell whether the server applied it.

    The request was sent but no answer came back (a timeout, a dropped connection), or a proxy
    answered with a 5xx for the backend. The mutation is not resent, since it could be applied
    twice: check its effect before running it again.

    It is a requests ConnectionError, what a mutation that timed out raised before, so existing
    `except requests.ConnectionError` and `except requests.RequestException` clauses catch it.

    Attributes:
        operation: the GraphQL field the mutation called.
        cause: the error the request failed with.
        index: when the mutation sent one batch of a longer list, the position in that list of
            the batch's first item. The batches before it were applied.
        external_ids: when an asset import sent one batch of the assets, the external ids of the
            assets in that batch. The batches before it were applied. An index would not locate
            it: the import filters and regroups the assets before sending them.
    """

    def __init__(
        self,
        operation: str,
        cause: BaseException,
        index: Optional[int] = None,
        external_ids: Optional[list[str]] = None,
    ) -> None:
        self.operation = operation
        self.cause = cause
        self.index = index
        self.external_ids = external_ids
        super().__init__(
            f"The request calling {operation} failed ({type(cause).__name__}: {cause}). It may"
            " have been processed by the server anyway, so it was not sent again. Check its"
            f" effect before retrying.{self._batch_message()}"
        )

    def _batch_message(self) -> str:
        if self.index is not None:
            return (
                f" The items before index {self.index} were applied; the batch starting at index"
                f" {self.index} may or may not have been, and the items after it were not sent."
            )
        if self.external_ids:
            shown = ", ".join(self.external_ids[:5])
            more = len(self.external_ids) - 5
            listed = f"{shown} and {more} more" if more > 0 else shown
            return (
                f" The earlier batches were applied; the batch of the assets {listed} may or may"
                " not have been, and the later ones were not sent."
            )
        return ""

    def __reduce__(self):
        """Rebuild from the attributes: args holds only the message, which __init__ cannot take.

        Without it, the error cannot be unpickled, so a process pool running a mutation that
        raised it breaks and loses the message. The message is kept as it was: the cause may
        lose details once unpickled (urllib3 drops the connection pool from its errors).
        """
        return (
            type(self),
            (self.operation, self.cause, self.index, self.external_ids),
            {"args": self.args},
        )

    def at_index(self, index: int) -> "MutationOutcomeUnknownError":
        """The same error, located in the caller's list of items."""
        return MutationOutcomeUnknownError(self.operation, self.cause, index=index)

    def for_assets(self, external_ids: list[str]) -> "MutationOutcomeUnknownError":
        """The same error, for the batch of assets with these external ids."""
        return MutationOutcomeUnknownError(self.operation, self.cause, external_ids=external_ids)


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


class DeprecatedArgumentError(ValueError):
    """Raised when the user gave an argument that is no longer supported."""
