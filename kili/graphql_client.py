import websocket
import threading
import random
import string
import json
import time
from datetime import datetime

from six.moves import urllib

from . import __version__


class GraphQLClient:
    def __init__(self, endpoint, session=None, verify=True):
        self.endpoint = endpoint
        self.headername = None
        self.session = session
        self.token = None
        self.verify = verify

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def inject_token(self, token, headername='Authorization'):
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'X-Powered-By': f'Kili Playground/{__version__}'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

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
                    raise Exception(req.content)
                raise exception

        req = urllib.request.Request(
            self.endpoint, json.dumps(data).encode('utf-8'), headers)
        try:
            response = urllib.request.urlopen(req)
            str_json = response.read().decode('utf-8')
            return json.loads(str_json)
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e


GQL_WS_SUBPROTOCOL = "graphql-ws"


class SubscriptionGraphQLClient:
    """
    A simple GraphQL client that works over Websocket as the transport
    protocol, instead of HTTP.
    This follows the Apollo protocol.
    https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md
    """

    def __init__(self, url):
        self.ws_url = url
        self._paused = False
        self._connect()
        self._subscription_running = False
        self._st_id = None

    def _connect(self):
        self._conn = websocket.create_connection(self.ws_url,
                                                 on_message=self._on_message,
                                                 subprotocols=[GQL_WS_SUBPROTOCOL])
        self._created_at = datetime.now()
        self._conn.on_message = self._on_message

    def _reconnect(self):
        self._connect()
        self._subscription_running = True

    def _on_message(self, message):
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
        _id = gen_id()
        frame = {'id': _id, 'type': 'start', 'payload': payload}
        self._conn.send(json.dumps(frame))
        return _id

    def _stop(self, _id):
        payload = {'id': _id, 'type': 'stop'}
        self._conn.send(json.dumps(payload))
        return self._conn.recv()

    def query(self, query, variables=None, headers=None):
        self._conn_init(headers)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _id = self._start(payload)
        res = self._conn.recv()
        self._stop(_id)
        return res

    def prepare_subscribe(self, query, variables, headers, callback, authorization):
        self._conn_init(headers, authorization)
        payload = {'headers': headers, 'query': query, 'variables': variables}
        _cc = self._on_message if not callback else callback
        _id = self._start(payload)
        self._id = _id
        return _cc, _id

    def subscribe(self, query, variables=None, headers=None, callback=None, authorization=None):
        _cc, _id = self.prepare_subscribe(
            query, variables, headers, callback, authorization)

        def subs(_cc, _id):
            total_reconnections = 0
            max_reconnections = 10
            self._subscription_running = True
            while self._subscription_running and total_reconnections < max_reconnections:
                try:
                    r = json.loads(self._conn.recv())
                    if r['type'] == 'error' or r['type'] == 'complete':
                        print(r)
                        self._stop_subscribe(_id)
                        break
                    elif r['type'] != 'ka' and not self._paused:
                        _cc(_id, r)
                    time.sleep(1)
                except websocket._exceptions.WebSocketConnectionClosedException as e:
                    print('Connection closed error : {}'.format(str(e)))
                    print(
                        f'Will try to reconnect {max_reconnections - total_reconnections} times...')
                    self._reconnect()
                    total_reconnections += 1
                    _cc, _id = self.prepare_subscribe(
                        query, variables, headers, callback, authorization)
                    continue
            print('Did not reconnect successfully...')

        self._st_id = threading.Thread(target=subs, args=(_cc, _id))
        self._st_id.start()
        return _id

    def _stop_subscribe(self, _id):
        self._subscription_running = False
        self._stop(_id)

    def close(self):
        self._conn.close()

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    def get_lifetime(self):
        return (datetime.now() - self._created_at).seconds

    def reset_timeout(self):
        self._reconnect()


# generate random alphanumeric id

def gen_id(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
