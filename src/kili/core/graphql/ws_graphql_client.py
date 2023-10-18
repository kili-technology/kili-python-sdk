"""WebsocketGraphQL Client."""

import json
import random
import string
import threading
import time
from datetime import datetime
from typing import Callable, Dict, Optional

import websocket
from typing_extensions import LiteralString

GQL_WS_SUBPROTOCOL = "graphql-ws"


class SubscriptionGraphQLClient:
    """A simple GraphQL client that works over Websocket as the transport protocol, instead of HTTP.

    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments

    def __init__(self, url) -> None:
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
        _cc = callback if callback else self._on_message
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
