"""GraphQL Client."""

import json
import logging
import os
import random
import string
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import urlparse

import graphql
import requests
import websocket
from filelock import FileLock
from gql import Client, gql
from gql.transport import exceptions
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as gql_requests_logger
from graphql import DocumentNode, print_schema
from pyrate_limiter import Duration, Limiter, RequestRate
from typing_extensions import LiteralString

from kili import __version__
from kili.core.constants import MAX_CALLS_PER_MINUTE
from kili.core.graphql.clientnames import GraphQLClientName
from kili.exceptions import GraphQLError
from kili.utils.logcontext import LogContext

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
        http_client: requests.Session,
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

        gql_requests_logger.setLevel(logging.WARNING)

        self._gql_transport = RequestsHTTPTransport(
            url=endpoint,
            headers=self._get_headers(),
            cookies=None,
            auth=None,
            use_json=True,
            timeout=30,
            verify=verify,
            retries=20,
            method="POST",
            retry_backoff_factor=0.5,
            # backend can return 401 errors even though we have a valid api key
            retry_status_forcelist=RequestsHTTPTransport._default_retry_codes + (401,),
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
            schema_str = print_schema(session.client.schema)  # type: ignore

        return schema_str

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
            version = response_json["version"]
            return version
        return None

    def execute(
        self, query: Union[str, DocumentNode], variables: Optional[Dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """Execute a query.

        Args:
            query: the GraphQL query
            variables: the payload of the query
            kwargs: additional arguments to pass to the GraphQL client
        """

        def _execute(
            document: DocumentNode, variables: Optional[Dict] = None, **kwargs
        ) -> Dict[str, Any]:
            try:
                with _limiter.ratelimit("GraphQLClient.execute", delay=True), _execute_lock:
                    result = self._gql_client.execute(
                        document=document,
                        variable_values=variables,
                        extra_args={
                            "headers": {
                                **self._gql_transport.headers,  # type: ignore
                                **LogContext(),
                            }
                        },
                        **kwargs,
                    )

            except graphql.GraphQLError as err:  # local validation error
                raise GraphQLError(error=err.message) from err
            except exceptions.TransportQueryError as err:  # graphql query refused by the backend
                raise GraphQLError(error=err.errors) from err

            return result

        document = query if isinstance(query, DocumentNode) else gql(query)

        try:
            return _execute(document, variables, **kwargs)

        except GraphQLError as err:
            # if error is due do parsing or local validation of the query (graphql.GraphQLError)
            # we refresh the schema and retry once
            if isinstance(err.__cause__, graphql.GraphQLError):
                self._purge_graphql_schema_cache_dir()
                self._gql_client = self._initizalize_graphql_client()
                return _execute(document, variables, **kwargs)  # if it fails again, we crash here

            raise err


GQL_WS_SUBPROTOCOL = "graphql-ws"


class SubscriptionGraphQLClient:
    """A simple GraphQL client that works over Websocket as the transport protocol, instead of HTTP.

    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments

    def __init__(self, url):
        self.ws_url = url
        self._id = None
        self._paused = False
        self._connect()
        self._subscription_running = False
        self._st_id = None
        self.failed_connection_attempts = 0

    def _connect(self):
        """Handles the connection."""
        self._conn = websocket.create_connection(
            self.ws_url, on_message=self._on_message, subprotocols=[GQL_WS_SUBPROTOCOL]
        )
        self._created_at = datetime.now()
        self._conn.on_message = self._on_message  # type: ignore

    def _reconnect(self):
        """Handles the reconnection."""
        self._connect()
        self._subscription_running = True
        dt_string = datetime.now().strftime(r"%d/%m/%Y %H:%M:%S")
        print(f"{dt_string} reconnected")
        self.failed_connection_attempts = 0

    def _on_message(self, message):
        """Handles messages.

        Args:
            message : the message
        """
        data = json.loads(message)
        # skip keepalive messages
        if data["type"] != "ka":
            print(message)

    def _conn_init(self, headers=None, authorization=None):
        """Initializes the websocket connection.

        Args:
            headers : Headers are necessary for Kili API v1
            authorization : Headers are necessary for Kili API v2
        """
        payload = {
            "type": "connection_init",
            "payload": {"headers": headers, "Authorization": authorization},
        }
        self._conn.send(json.dumps(payload).encode("utf-8"))
        self._conn.recv()

    def _start(self, payload):
        """Handles start.

        Args:
            payload
        """
        _id = gen_id()
        frame = {"id": _id, "type": "start", "payload": payload}
        self._conn.send(json.dumps(frame).encode("utf-8"))
        return _id

    def _stop(self, _id):
        """Handles stop.

        Args:
        - _id: connection id
        """
        payload = {"id": _id, "type": "stop"}
        self._conn.send(json.dumps(payload).encode("utf-8"))
        return self._conn.recv()

    def query(self, query: str, variables: Optional[Dict] = None, headers: Optional[Dict] = None):
        """Sends a query.

        Args:
            query: the GraphQL query
            variables: the payload of the query
            headers: headers
        """
        self._conn_init(headers)
        payload = {"headers": headers, "query": query, "variables": variables}
        _id = self._start(payload)
        res = self._conn.recv()
        self._stop(_id)
        return res

    def prepare_subscribe(
        self,
        query: str,
        variables: Optional[Dict],
        headers: Optional[Dict],
        callback: Optional[Callable],
        authorization: Optional[str],
    ):
        """Prepares a subscription.

        Args:
            query: the GraphQL query
            variables: the payload of the query
            headers: headers
            callback: function executed after the subscription
            authorization: authorization header
        """
        self._conn_init(headers, authorization)
        payload = {"headers": headers, "query": query, "variables": variables}
        _cc = self._on_message if not callback else callback
        _id = self._start(payload)
        self._id = _id
        return _cc, _id

    def subscribe(
        self,
        query: str,
        variables: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        callback: Optional[Callable] = None,
        authorization: Optional[str] = None,
    ):
        """Subscribes.

        Args:
            query: the GraphQL query
            variables: the payload of the query
            headers: headers
            callback: function executed after the subscription
            authorization: authorization header
        """
        _cc, _id = self.prepare_subscribe(query, variables, headers, callback, authorization)

        def subs(_cc, _id):
            max_reconnections = 10
            self._subscription_running = True
            while (
                self._subscription_running and self.failed_connection_attempts < max_reconnections
            ):
                try:
                    response = json.loads(self._conn.recv())
                    if response["type"] == "error" or response["type"] == "complete":
                        print(response)
                        self._stop_subscribe(_id)
                        break
                    if response["type"] != "ka" and not self._paused:
                        _cc(_id, response)  # type:ignore
                    time.sleep(1)
                except (
                    websocket._exceptions.WebSocketConnectionClosedException  # pylint: disable=protected-access
                ) as error:
                    self.failed_connection_attempts += 1
                    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    error_message = str(error)
                    print(f"{dt_string} Connection closed error : {error_message}")
                    print(
                        "Will try to reconnect"
                        f" {max_reconnections - self.failed_connection_attempts} times..."
                    )
                    self._reconnect()
                    _cc, _id = self.prepare_subscribe(
                        query, variables, headers, callback, authorization
                    )
                    continue
            print(f"Did not reconnect successfully after {max_reconnections} attempts")

        self._st_id = threading.Thread(target=subs, args=(_cc, _id))
        self._st_id.start()
        return _id

    def _stop_subscribe(self, _id):
        self._subscription_running = False
        self._stop(_id)

    def close(self):
        """Handles close."""
        self._conn.close()

    def pause(self):
        """Handles pause."""
        self._paused = True

    def unpause(self):
        """Handles unpause."""
        self._paused = False

    def get_lifetime(self):
        """Return the lifetime."""
        return (datetime.now() - self._created_at).seconds

    def reset_timeout(self):
        """Resets the timeout."""
        self._reconnect()


def gen_id(size: int = 6, chars: LiteralString = string.ascii_letters + string.digits) -> str:
    """Generate random alphanumeric id.

    Args:
        size: length of the id
        chars: chars used to generate the id
    """
    return "".join(random.choice(chars) for _ in range(size))
