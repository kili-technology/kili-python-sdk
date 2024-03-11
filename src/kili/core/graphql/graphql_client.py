"""GraphQL Client."""

import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import graphql
from filelock import FileLock
from gql import Client, gql
from gql.transport import exceptions
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as gql_requests_logger
from graphql import DocumentNode, print_schema
from pyrate_limiter import Duration, RequestRate
from pyrate_limiter.limiter import Limiter
from tenacity import (
    retry,
    retry_all,
    retry_any,
    retry_if_exception_message,
    retry_if_exception_type,
    retry_if_not_exception_message,
    stop_after_delay,
    wait_exponential,
)

import kili.exceptions
from kili import __version__
from kili.adapters.http_client import HttpClient
from kili.core.constants import MAX_CALLS_PER_MINUTE
from kili.core.graphql.clientnames import GraphQLClientName
from kili.utils.logcontext import LogContext

gql_requests_logger.setLevel(logging.WARNING)

# _limiter and _execute_lock must be kept at module-level
# they need to be shared between all instances of Kili client within the same process

# rate limiter to avoid sending too many queries to the backend
_limiter = Limiter(RequestRate(MAX_CALLS_PER_MINUTE, Duration.MINUTE))

# mutex to avoid multiple threads sending queries to the backend at the same time
_execute_lock = threading.Lock()

DEFAULT_GRAPHQL_SCHEMA_CACHE_DIR = Path.home() / ".cache" / "kili" / "graphql"


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class GraphQLClient:
    """GraphQL client."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        client_name: GraphQLClientName,
        http_client: HttpClient,
        verify: Union[bool, str] = True,
        enable_schema_caching: bool = True,
        graphql_schema_cache_dir: Optional[Union[str, Path]] = DEFAULT_GRAPHQL_SCHEMA_CACHE_DIR,
    ) -> None:
        """Initialize the GraphQL client.

        Args:
            endpoint: Kili API endpoint.
            api_key: Kili API key.
            client_name: Name of the client.
            http_client: HTTP client.
            verify: Whether to verify the SSL certificate.
            enable_schema_caching: Whether to cache the GraphQL schema on disk.
            graphql_schema_cache_dir: Directory where to cache the GraphQL schema.
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.client_name = client_name
        self.http_client = http_client
        self.verify = verify
        self.enable_schema_caching = enable_schema_caching
        self.graphql_schema_cache_dir = (
            Path(graphql_schema_cache_dir) if graphql_schema_cache_dir else None
        )

        self.ws_endpoint = self.endpoint.replace("http", "ws")

        self._gql_transport = RequestsHTTPTransport(
            url=endpoint,
            headers=self._get_headers(),
            timeout=30,
            verify=verify,
            retries=10,
            retry_backoff_factor=0.1,  # last retry will take 0.1*2**10 = 100s
            retry_status_forcelist=(
                429,  # 429 Too Many Requests
                502,  # 502 Bad Gateway
                503,  # 503 Service Unavailable
                504,  # 504 Gateway Timeout
            ),
        )

        if self.enable_schema_caching is True:
            if self.graphql_schema_cache_dir is None:
                raise ValueError(
                    "You must specify a cache directory if you want to enable schema caching."
                )

            self.graphql_schema_cache_dir.mkdir(parents=True, exist_ok=True)

            # mutex to avoid multiple processes operating in cache directory at the same time
            self._cache_dir_lock = FileLock(
                self.graphql_schema_cache_dir / "cache_dir.lock", timeout=15
            )

        self._gql_client = self._initizalize_graphql_client()

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers."""
        return {
            "Authorization": f"X-API-Key: {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "apollographql-client-name": self.client_name.value,
            "apollographql-client-version": __version__,
        }

    @staticmethod
    def _get_introspection_args() -> Dict[str, bool]:
        """Get the introspection arguments."""
        return {
            "descriptions": True,  # descriptions for the schema, types, fields, and arguments
            "specified_by_url": False,  # https://spec.graphql.org/draft/#sec--specifiedBy
            "directive_is_repeatable": True,  # include repeatability of directives
            "schema_description": True,  # include schema description
            "input_value_deprecation": True,  # request deprecated input fields
        }

    def _initizalize_graphql_client(self) -> Client:
        """Initialize the GraphQL client."""
        if os.environ.get("KILI_SDK_SKIP_CHECKS", None) is not None:
            return Client(
                transport=self._gql_transport,
                fetch_schema_from_transport=False,
                introspection_args=self._get_introspection_args(),
            )

        if self.enable_schema_caching is False:
            return Client(
                transport=self._gql_transport,
                fetch_schema_from_transport=True,
                introspection_args=self._get_introspection_args(),
            )

        # In some cases (local development), we cannot get the kili version from the backend
        # and therefore we cannot determine the schema version, so we don't cache the schema
        graphql_schema_path = self._get_graphql_schema_path()
        if graphql_schema_path is None:
            return Client(
                transport=self._gql_transport,
                fetch_schema_from_transport=True,
                introspection_args=self._get_introspection_args(),
            )

        with self._cache_dir_lock:
            if not (graphql_schema_path.is_file() and graphql_schema_path.stat().st_size > 0):
                self._purge_graphql_schema_cache_dir()  # delete old schema files
                schema_str = self._get_graphql_schema_from_endpoint()
                self._cache_graphql_schema(graphql_schema_path, schema_str)

            else:
                schema_str = graphql_schema_path.read_text(encoding="utf-8")

        return Client(
            transport=self._gql_transport,
            schema=schema_str,
            introspection_args=self._get_introspection_args(),
        )

    def _get_graphql_schema_from_endpoint(self) -> str:
        """Get the GraphQL schema from the endpoint."""
        with Client(
            transport=self._gql_transport,
            fetch_schema_from_transport=True,
            introspection_args=self._get_introspection_args(),
        ) as session:
            return print_schema(session.client.schema)  # pyright: ignore[reportGeneralTypeIssues]

    def _cache_graphql_schema(self, graphql_schema_path: Path, schema_str: str) -> None:
        """Cache the graphql schema on disk."""
        with self._cache_dir_lock, graphql_schema_path.open("w", encoding="utf-8") as file:
            file.write(schema_str)
            file.flush()

    def _purge_graphql_schema_cache_dir(self) -> None:
        """Purge the schema cache directory."""
        if self.graphql_schema_cache_dir is None:
            return

        with self._cache_dir_lock:
            for file in self.graphql_schema_cache_dir.glob("*.graphql"):
                file.unlink()

    def _get_graphql_schema_path(self) -> Optional[Path]:
        """Get the path of the GraphQL schema.

        Will return None if we cannot get the schema version.
        """
        if self.graphql_schema_cache_dir is None:
            return None

        endpoint_netloc = urlparse(self.endpoint).netloc
        version = self._get_kili_app_version()
        if version is None:
            return None
        filename = f"{endpoint_netloc}_{version}.graphql"
        return self.graphql_schema_cache_dir / filename

    def _get_kili_app_version(self) -> Optional[str]:
        """Get the version of the Kili app server.

        Returns None if the version cannot be retrieved.
        """
        url = self.endpoint.replace("/graphql", "/version")
        response = self.http_client.get(url, timeout=30)
        if response.status_code == 200 and '"version":' in response.text:
            response_json = response.json()
            return response_json["version"]
        return None

    @classmethod
    def _remove_nullable_inputs(cls, variables: Dict) -> Dict:
        """Remove nullable inputs from the variables."""
        for key in ("data", "where", "project", "asset", "label", "issue"):
            if key in variables and isinstance(variables[key], dict):
                variables[key] = cls._remove_nullable_inputs(variables[key])

        return {k: v for k, v in variables.items() if v is not None}

    def execute(
        self, query: Union[str, DocumentNode], variables: Optional[Dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """Execute a query.

        Args:
            query: the GraphQL query
            variables: the payload of the query
            kwargs: additional arguments to pass to the GraphQL client
        """
        document = query if isinstance(query, DocumentNode) else gql(query)
        variables = self._remove_nullable_inputs(variables) if variables else None

        try:
            return self._execute_with_retries(document, variables, **kwargs)

        except graphql.GraphQLError:  # local validation error
            # the local schema might be outdated
            # we refresh the schema and retry once
            self._purge_graphql_schema_cache_dir()
            self._gql_client = self._initizalize_graphql_client()
            try:
                return self._execute_with_retries(document, variables, **kwargs)

            except graphql.GraphQLError as err:
                # even after updating the schema, the query is invalid , we crash
                raise kili.exceptions.GraphQLError(error=err.message) from err

            # the query is valid but the server refused it, we crash
            except exceptions.TransportQueryError as err:
                raise kili.exceptions.GraphQLError(error=err.errors) from err

        except exceptions.TransportQueryError as err:  # remove validation error
            # the server refused the query after some retries, we crash
            raise kili.exceptions.GraphQLError(error=err.errors) from err

    @retry(
        reraise=True,  # re-raise the last exception
        retry=retry_all(
            retry_if_exception_type(  # error received from server
                (exceptions.TransportQueryError, exceptions.TransportServerError)
            ),
            retry_if_not_exception_message(
                match=r'.*Variable "(\$\w+)" of required type "(\w+!)" was not provided.*'
            ),
            retry_if_not_exception_message(match=r'.*Variable "(\$\w+)" got invalid value .*'),
            retry_if_not_exception_message(
                match=r'.*Field "(\w+)" is not defined by type "(\w+)".*'
            ),
            retry_any(
                retry_if_exception_message(match=r".*Invalid request made to Flagsmith API.*"),
                retry_if_exception_message(match=r".*Failed to fetch data connection.*"),
                retry_if_exception_message(match=r".*Unauthorized for url.*"),
            ),
        ),
        stop=stop_after_delay(3 * 60),
        wait=wait_exponential(multiplier=0.5, min=1, max=10),
    )
    def _execute_with_retries(
        self, document: DocumentNode, variables: Optional[Dict], **kwargs
    ) -> Dict[str, Any]:
        return self._raw_execute(document, variables, **kwargs)

    def _raw_execute(
        self, document: DocumentNode, variables: Optional[Dict], **kwargs
    ) -> Dict[str, Any]:
        with _limiter.ratelimit("GraphQLClient.execute", delay=True), _execute_lock:
            return self._gql_client.execute(
                document=document,
                variable_values=variables,
                extra_args={
                    "headers": {
                        **(self._gql_transport.headers or {}),
                        **LogContext(),
                    }
                },
                **kwargs,
            )
