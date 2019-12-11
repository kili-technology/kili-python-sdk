import json
import time

from six.moves import urllib


class GraphQLClient:
    def __init__(self, endpoint, session=None):
        self.endpoint = endpoint
        self.session = session
        self.token = None
        self.headername = None

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def inject_token(self, token, headername='Authorization'):
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        if self.session is not None:
            try:
                number_of_trials = 3
                for n in range(number_of_trials):
                    req = self.session.post(self.endpoint, json.dumps(
                        data).encode('utf-8'), headers=headers)
                    if req.status_code == 200:
                        break
                    time.sleep(1)
                return req.json()
            except Exception as e:
                print('Request failed with error:\n')
                if req:
                    print(req.content)
                print('')
                raise e

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
