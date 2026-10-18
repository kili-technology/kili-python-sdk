"""What the GraphQL client retries, and when.

Every mutation is treated as non-idempotent: it is resent only when the server certainly did not
run it. When the outcome is unknown (the request was sent but no answer came back, or a proxy
answered for the backend), resending could apply it twice, so the error is raised instead.
Queries have no side effect and are also retried on those unknown outcomes, a bounded number of
times since each retry makes the backend do the work again.
"""

import re
from enum import Enum
from typing import Optional

import requests
from gql.transport import exceptions
from graphql import DocumentNode, FieldNode, OperationDefinitionNode, OperationType
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import (
    ConnectTimeout,
    InvalidHeader,
    InvalidJSONError,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    ProxyError,
    ReadTimeout,
    RequestException,
    SSLError,
    URLRequired,
)
from urllib3.exceptions import (
    ConnectTimeoutError,
    MaxRetryError,
    NewConnectionError,
    ReadTimeoutError,
)

# Longest wait for a server that rejects requests before processing them: refused connections,
# while a backend instance is being replaced, come in episodes of under a minute.
RETRY_DEADLINE_SECONDS = 2 * 60
# Attempts when the outcome is unknown or the error transient: queries only, see should_retry.
MAX_ATTEMPTS_ON_UNCERTAIN_OUTCOME = 5
# A gateway that gave up on the backend: the request was heavy, resending it costs the backend
GATEWAY_TIMEOUT_STATUSES = frozenset({504, 524})
MAX_BACKOFF_SECONDS = 30
MAX_RETRY_AFTER_SECONDS = 60

# Rejected before any resolver ran: 401 by the authentication middleware, which runs before the
# body is parsed, 429 by rate limiting, 521 by Cloudflare when the origin refused the connection.
# Cloudflare's 522 is not in it: it also covers a request sent that the origin never acknowledged.
NOT_PROCESSED_STATUSES = frozenset({401, 429, 521})

# Envoy answers 503 both when it could not reach a backend pod and when the pod closed the
# connection after receiving the request. Only the first kind is safe to resend; it is told apart
# by the body Envoy writes. Most backend 503s are of the second kind.
ENVOY_NOT_FORWARDED_503 = re.compile(
    r"no healthy upstream|reset reason: (?:overflow|(?:remote )?connection failure)"
)

# Errors raised by requests while building the request, before anything is sent.
_INVALID_REQUEST_ERRORS = (
    InvalidJSONError,
    InvalidHeader,
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    URLRequired,
)

# Errors returned by the backend that go away on their own. The resolver ran, so only queries
# retry them.
TRANSIENT_GRAPHQL_ERRORS = (
    re.compile(r".*Invalid request made to Flagsmith API.*"),
    re.compile(r".*Failed to fetch data connection.*"),
)


class Outcome(Enum):
    """What a failed request tells about the server's state."""

    NOT_PROCESSED = "not_processed"  # safe to resend anything
    UNKNOWN = "unknown"  # the server may have run the operation
    TRANSIENT = "transient"  # the server ran it and returned a known temporary error
    FAILED = "failed"  # a definite error: resending gives the same answer


def classify(error: BaseException) -> Outcome:  # pylint: disable=too-many-return-statements
    """Tell whether the server may have run the operation that raised this error."""
    if isinstance(error, _INVALID_REQUEST_ERRORS):
        return Outcome.FAILED
    if _request_never_sent(error):
        return Outcome.NOT_PROCESSED
    if isinstance(error, exceptions.TransportServerError):
        return _classify_status(error)
    if isinstance(error, exceptions.TransportQueryError):
        message = str(error)
        if any(pattern.match(message) for pattern in TRANSIENT_GRAPHQL_ERRORS):
            return Outcome.TRANSIENT
        return Outcome.FAILED
    if isinstance(error, SSLError) and "certificate" in str(error).lower():
        return Outcome.FAILED  # an untrusted certificate stays untrusted
    if isinstance(error, (RequestException, exceptions.TransportProtocolError)):
        return Outcome.UNKNOWN  # read timeout, connection reset after sending, truncated answer
    return Outcome.FAILED


def _classify_status(error: exceptions.TransportServerError) -> Outcome:
    if error.code in NOT_PROCESSED_STATUSES:
        return Outcome.NOT_PROCESSED
    if error.code == 503:
        response = http_response(error)
        if (
            response is not None
            # "retried and the latest reset reason": Envoy had forwarded the request before
            and "retried" not in response.text
            and ENVOY_NOT_FORWARDED_503.search(response.text)
        ):
            return Outcome.NOT_PROCESSED
        return Outcome.UNKNOWN
    if error.code is not None and error.code >= 500:
        return Outcome.UNKNOWN  # 502/504/52x can come from a proxy after the backend ran
    return Outcome.FAILED


def is_overload(error: BaseException) -> bool:
    """Whether the request may have been too heavy for the server: a lighter one could pass.

    A timeout, a reset or a 5xx after the request reached the backend, or a 413. A request the
    server did not process says nothing about its weight: a 429, a 503 Envoy could not forward.
    """
    if isinstance(error, exceptions.TransportServerError) and error.code == 413:
        return True
    return classify(error) is Outcome.UNKNOWN


def attempts_allowed(error: BaseException, mutation: bool) -> Optional[int]:
    """How many attempts an operation that failed with this error gets, None for no limit.

    A request the server did not process is resent until the deadline. A mutation that may have
    been processed is never resent. A query is, a few times, except when the server itself
    failed (500) or did not answer in time (a read timeout, a gateway's 504, Cloudflare's 524):
    resending makes it redo the work, so it gets one more attempt at most.
    """
    outcome = classify(error)
    if outcome is Outcome.NOT_PROCESSED:
        return None
    if mutation or outcome is Outcome.FAILED:
        return 1
    code = error.code if isinstance(error, exceptions.TransportServerError) else None
    if code == 500:
        return 1
    if code in GATEWAY_TIMEOUT_STATUSES or _is_read_timeout(error):
        return 2
    return MAX_ATTEMPTS_ON_UNCERTAIN_OUTCOME


def _is_read_timeout(error: BaseException) -> bool:
    """Whether no answer came in time, before its headers (ReadTimeout) or during its body."""
    if isinstance(error, ReadTimeout):
        return True
    # a stall while reading the body reaches requests' caller as a ConnectionError
    cause = error.args[0] if isinstance(error, RequestsConnectionError) and error.args else None
    return isinstance(cause, ReadTimeoutError)


def should_retry(error: BaseException, mutation: bool) -> bool:
    """Whether the operation that raised this error can be sent again."""
    return attempts_allowed(error, mutation) != 1


def _request_never_sent(error: BaseException) -> bool:
    if isinstance(error, ConnectTimeout):
        return True
    if isinstance(error, ProxyError):
        return _proxy_never_reached(error)
    if isinstance(error, RequestsConnectionError) and error.args:
        cause = error.args[0]
        # a refused connection or a failed DNS resolution, before any byte was sent
        return isinstance(cause, MaxRetryError) and isinstance(cause.reason, NewConnectionError)
    return False


def _proxy_never_reached(error: ProxyError) -> bool:
    """Whether the proxy failed before the request was sent through it.

    urllib3 also raises ProxyError for a connection that drops after the request was sent: closing
    the connection resets its "connected to the proxy" flag. Only a failure to connect to the proxy
    or to open the tunnel means the request never left.
    """
    cause = error.args[0] if error.args else None
    if isinstance(cause, MaxRetryError):
        cause = cause.reason
    original = getattr(cause, "original_error", None)
    if isinstance(original, (NewConnectionError, ConnectTimeoutError)):
        return True
    return isinstance(original, OSError) and str(original).startswith("Tunnel connection failed")


def http_response(error: BaseException) -> Optional[requests.Response]:
    """The HTTP response behind a gql TransportServerError, if any."""
    cause = error.__cause__
    return cause.response if isinstance(cause, requests.HTTPError) else None


def retry_after_seconds(error: BaseException) -> Optional[float]:
    """Seconds the server asked to wait before a retry, from its Retry-After header."""
    response = http_response(error)
    return parse_retry_after(response.headers.get("Retry-After")) if response is not None else None


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Seconds from a Retry-After header given in seconds.

    HTTP dates are ignored.
    """
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return min(max(seconds, 0.0), MAX_RETRY_AFTER_SECONDS)


def describe(error: BaseException) -> str:
    """Short reason for a failed request, for log messages."""
    if isinstance(error, exceptions.TransportServerError) and error.code is not None:
        return f"HTTP {error.code}"
    return type(error).__name__


def is_mutation(document: DocumentNode) -> bool:
    """Whether the document runs a mutation."""
    return any(
        isinstance(definition, OperationDefinitionNode)
        and definition.operation == OperationType.MUTATION
        for definition in getattr(document, "definitions", ())
    )


def operation_name(document: DocumentNode) -> str:
    """Name of the root field the document calls, for messages."""
    for definition in getattr(document, "definitions", ()):
        if isinstance(definition, OperationDefinitionNode):
            for selection in definition.selection_set.selections:
                if isinstance(selection, FieldNode):
                    return selection.name.value
    return "the operation"
