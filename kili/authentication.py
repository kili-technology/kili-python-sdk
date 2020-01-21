import os
import warnings

import requests

from . import __version__
from .graphql_client import GraphQLClient
from .mutations.user import signin

warnings.simplefilter('always')
warnings.filterwarnings('ignore', category=ImportWarning)

MAX_RETRIES = 20


def authenticate(email,
                 password=os.getenv('KILI_USER_PASSWORD'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/graphql'):
    message = '''Deprecated: authenticate has been renamed, and is not recommended for use.
Use instead:
  from kili.authentication import KiliAuth
  from kili.playground import Playground
  kauth = KiliAuth()
  playground = Playground(kauth)
  assets = playground.export_assets(project_id)'''

    warnings.warn(message, DeprecationWarning)

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    client = GraphQLClient(api_endpoint, session)

    auth_payload = signin(client, email, password)
    api_token = auth_payload['token']
    client.inject_token('Bearer: ' + api_token)
    user_id = auth_payload['user']['id']
    return client, user_id


class KiliAuth(object):
    """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth()
    playground = Playground(kauth)
    assets = playground.export_assets(project_id)
    """

    def __init__(self,
                 email=os.getenv('KILI_USER_EMAIL'),
                 password=os.getenv('KILI_USER_PASSWORD'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/graphql'):
        self.session = requests.Session()

        self.check_versions_match(api_endpoint)

        adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.client = GraphQLClient(api_endpoint, self.session)
        auth_payload = signin(self.client, email, password)
        api_token = auth_payload['token']
        self.client.inject_token('Bearer: ' + api_token)
        self.user_id = auth_payload['user']['id']

    def __del__(self):
        self.session.close()

    @staticmethod
    def check_versions_match(api_endpoint):
        url = api_endpoint.replace('/graphql', '/version')
        response = requests.get(url).json()
        version = response['version']
        if version != __version__:
            message = 'Kili Playground version should match with Kili API version.\n' + \
                      f'Please install version: "pip install kili=={version}"'
            warnings.warn(message, UserWarning)
