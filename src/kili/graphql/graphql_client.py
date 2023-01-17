"""
GraphQL Client
"""


import json
import os
import random
import string
import threading
import time
import urllib
from datetime import datetime
from enum import Enum
from typing import Dict

import websocket

from kili import __version__


class GraphQLClientName(Enum):  # pylint: disable=too-few-public-methods
    """GraphQL client name."""

    SDK = "python-sdk"
    CLI = "python-cli"


class GraphQLClient:
    """
    A simple GraphQL client
    """

    def __init__(
        self,
        endpoint,
        client_name: GraphQLClientName,
        session=None,
        verify=True,
    ):
        self.endpoint = endpoint
        self.client_name = client_name
        self.headername = None
        self.session = session
        self.token = None
        self.verify = verify

    def execute(self, query, variables=None) -> Dict:
        """
        Execute a query

        Args:
            query
            variables
        """
        return self._send(query, variables)

    def inject_token(self, token, headername="Authorization"):
        """Inject a token.

        Args:
            token
            headername:
        """
        self.token = token
        self.headername = headername

    def _send(self, query, variables) -> Dict:
        """
        Send the query

        Args:
            query
            variables
        """
        data = {"query": query, "variables": variables}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "apollographql-client-name": self.client_name.value,
            "apollographql-client-version": __version__,
        }

        if self.token is not None:
            if self.headername:
                headers[self.headername] = f"{self.token}"
            else:
                raise ValueError("headername must be defined.")

        if self.session is not None:
            req = None
            try:
                try:
                    number_of_trials = int(os.getenv("KILI_SDK_TRIALS_NUMBER", "10"))
                except ValueError:
                    number_of_trials = 10
                for _ in range(number_of_trials):
                    self.session.verify = self.verify
                    req = self.session.post(
                        self.endpoint, json.dumps(data).encode("utf-8"), headers=headers
                    )
                    errors_in_response = "errors" in req.json()
                    bad_request_error = req.status_code == 400 and errors_in_response
                    sucessful_request = req.status_code == 200 and not errors_in_response
                    if sucessful_request or bad_request_error:
                        break
                    if req.status_code == 401:
                        raise Exception("Invalid API KEY")
                    time.sleep(1)
                return req.json()  # type:ignore X
            except Exception as exception:
                if req is not None:
                    raise Exception(req.content) from exception
                raise exception

        req = urllib.request.Request(  # type: ignore
            self.endpoint, json.dumps(data).encode("utf-8"), headers
        )
        try:
            with urllib.request.urlopen(req) as response:  # type:ignore
                str_json = response.read().decode("utf-8")
                return json.loads(str_json)
        except urllib.error.HTTPError as error:  # type:ignore
            print((error.read()))
            print("")
            raise error


GQL_WS_SUBPROTOCOL = "graphql-ws"


class SubscriptionGraphQLClient:
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
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
        """
        Handles the connection
        """
        # pylint: disable=no-member
        self._conn = websocket.create_connection(
            self.ws_url, on_message=self._on_message, subprotocols=[GQL_WS_SUBPROTOCOL]
        )
        self._created_at = datetime.now()
        self._conn.on_message = self._on_message

    def _reconnect(self):
        """
        Handles the reconnection
        """
        self._connect()
        self._subscription_running = True
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"{dt_string} reconnected")
        self.failed_connection_attempts = 0

    def _on_message(self, message):
        """
        Handles messages

        Args:
            message : the message
        """
        data = json.loads(message)
        # skip keepalive messages
        if data["type"] != "ka":
            print(message)

    def _conn_init(self, headers=None, authorization=None):
        """
        Initializes the websocket connection

        Args:
            headers : Headers are necessary for Kili API v1
            authorization : Headers are necessary for Kili API v2
        """
        payload = {
            "type": "connection_init",
            "payload": {"headers": headers, "Authorization": authorization},
        }
        self._conn.send(json.dumps(payload))
        self._conn.recv()

    def _start(self, payload):
        """
        Handles start

        Args:
            payload
        """
        _id = gen_id()
        frame = {"id": _id, "type": "start", "payload": payload}
        self._conn.send(json.dumps(frame))
        return _id

    def _stop(self, _id):
        """
        Handles stop

        Args:
        - _id: connection id
        """
        payload = {"id": _id, "type": "stop"}
        self._conn.send(json.dumps(payload))
        return self._conn.recv()

    def query(self, query, variables=None, headers=None):
        """
        Sends a query

        Args:
            query
            variables
            headers
        """
        self._conn_init(headers)
        payload = {"headers": headers, "query": query, "variables": variables}
        _id = self._start(payload)
        res = self._conn.recv()
        self._stop(_id)
        return res

    def prepare_subscribe(self, query, variables, headers, callback, authorization):
        """
        Prepares a subscription

        Args:
            query
            variables
            headers
            callback: function executed after the subscription
            authorization: authorization header
        """
        self._conn_init(headers, authorization)
        payload = {"headers": headers, "query": query, "variables": variables}
        _cc = self._on_message if not callback else callback
        _id = self._start(payload)
        self._id = _id
        return _cc, _id

    def subscribe(self, query, variables=None, headers=None, callback=None, authorization=None):
        """
        Subscribes

        Args:
            query
            variables
            headers
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
                    websocket._exceptions.WebSocketConnectionClosedException  # pylint: disable=no-member,protected-access
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
        """
        Handles close
        """
        self._conn.close()

    def pause(self):
        """
        Handles pause
        """
        self._paused = True

    def unpause(self):
        """
        Handles unpause
        """
        self._paused = False

    def get_lifetime(self):
        """
        Return the lifetime
        """
        return (datetime.now() - self._created_at).seconds

    def reset_timeout(self):
        """
        Resets the timeout
        """
        self._reconnect()


def gen_id(size=6, chars=string.ascii_letters + string.digits):
    """
    Generate random alphanumeric id

    Args:
        size: length of the id
        chars: chars used to generate the id
    """
    return "".join(random.choice(chars) for _ in range(size))
