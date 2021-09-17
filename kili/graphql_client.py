"""
GraphQL Client
"""

from datetime import datetime
import json
import random
import string
import threading
import time
import websocket

from six.moves import urllib

from . import __version__


class GraphQLClient:
    """
    A simple GraphQL client
    """

    def __init__(self, endpoint, session=None, verify=True):
        self.endpoint = endpoint
        self.headername = None
        self.session = session
        self.token = None
        self.verify = verify

    def execute(self, query, variables=None):
        """
        Execute a query

        Parameters
        ----------
        - query
        - variables
        """
        return self._send(query, variables)

    def inject_token(self, token, headername='Authorization'):
        """
        Inject a token

        Parameters
        ----------
        - token
        - headername: by default "Authorization"
        """
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        """
        Send the query

        Parameters
        ----------
        - query
        - variables
        """
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'X-Powered-By': f'Kili Playground/{__version__}'}

        if self.token is not None:
            headers[self.headername] = f'{self.token}'

        if self.session is not None:
            try:
                number_of_trials = 10
                for _ in range(number_of_trials):
                    self.session.verify = self.verify
                    req = self.session.post(self.endpoint, json.dumps(
                        data).encode('utf-8'), headers=headers)
                    if req.status_code == 200 and 'errors' not in req.json():
                        break
                    time.sleep(1)
                return req.json()
            except Exception as exception:
                if req is not None:
                    raise Exception(req.content) from exception
                raise exception

        req = urllib.request.Request(
            self.endpoint, json.dumps(data).encode('utf-8'), headers)
        try:
            with urllib.request.urlopen(req) as response:
                str_json = response.read().decode('utf-8')
                return json.loads(str_json)
        except urllib.error.HTTPError as error:
            print((error.read()))
            print('')
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
        self._conn = websocket.create_connection(self.ws_url,
                                                 on_message=self._on_message,
                                                 subprotocols=[GQL_WS_SUBPROTOCOL])
        self._created_at = datetime.now()
        self._conn.on_message = self._on_message

    def _reconnect(self):
        """
        Handles the reconnection
        """
        self._connect()
        self._subscription_running = True
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f'{dt_string} reconnected')
        self.failed_connection_attempts = 0

    def _on_message(self, message):
        """
        Handles messages

        Parameters
        ----------
        - message : the message
        """
        # pylint: disable=no-self-use
        data = json.loads(message)
        # skip keepalive messages
        if data['type'] != 'ka':
            print(message)

    def _conn_init(self, headers=None, authorization=None):
        """
        Initializes the websocket connection

        Parameters
        ----------
        - headers : Headers are necessary for Kili API v1
        - authorization : Headers are necessary for Kili API v2
        """
        payload = {
            'type': 'connection_init',
            'payload': {'headers': headers, 'Authorization': authorization}
        }
        self._conn.send(json.dumps(payload))
        self._conn.recv()

    def _start(self, payload):
        """
        Handles start

        Parameters
        ----------
        - payload
        """
        _id = gen_id()
        frame = {'id': _id, 'type': 'start', 'payload': payload}
        self._conn.send(json.dumps(frame))
        return _id

    def _stop(self, _id):
        """
        Handles stop

        Parameters
        ----------
        - _id: connection id
        """
        payload = {'id': _id, 'type': 'stop'}
        self._conn.send(json.dumps(payload))
        return self._conn.recv()

    def query(self, query, variables=None, headers=None):
        """
        Sends a query

        Parameters
        ----------
        - query
        - variables
        - headers
        """
        self._conn_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _id = self._start(payload)
        res = self._conn.recv()
        self._stop(_id)
        return res

    def prepare_subscribe(self, query, variables, headers, callback, authorization):
        """
        Prepares a subscription

        Parameters
        ----------
        - query
        - variables
        - headers
        - callback: function executed after the subscription
        - authorization: authorization header
        """
        self._conn_init(headers, authorization)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _cc = self._on_message if not callback else callback
        _id = self._start(payload)
        self._id = _id
        return _cc, _id

    def subscribe(self, query, variables=None, headers=None, callback=None, authorization=None):
        """
        Subscribes

        Parameters
        ----------
        - query
        - variables
        - headers
        - callback: function executed after the subscription
        - authorization: authorization header
        """
        _cc, _id = self.prepare_subscribe(
            query, variables, headers, callback, authorization)

        def subs(_cc, _id):
            max_reconnections = 10
            self._subscription_running = True
            while self._subscription_running \
                    and self.failed_connection_attempts < max_reconnections:
                try:
                    response = json.loads(self._conn.recv())
                    if response['type'] == 'error' or response['type'] == 'complete':
                        print(response)
                        self._stop_subscribe(_id)
                        break
                    if response['type'] != 'ka' and not self._paused:
                        _cc(_id, response)
                    time.sleep(1)
                except websocket._exceptions.WebSocketConnectionClosedException as error:  # pylint: disable=no-member,protected-access
                    self.failed_connection_attempts += 1
                    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    error_message = str(error)
                    print(f'{dt_string} Connection closed error : {error_message}')
                    print(
                        'Will try to reconnect'
                        f' {max_reconnections - self.failed_connection_attempts} times...')
                    self._reconnect()
                    _cc, _id = self.prepare_subscribe(
                        query, variables, headers, callback, authorization)
                    continue
            print(
                f'Did not reconnect successfully after {max_reconnections} attempts')

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

    Parameters
    ----------
    - size: length of the id
    - chars: chars used to generate the id
    """
    return ''.join(random.choice(chars) for _ in range(size))
