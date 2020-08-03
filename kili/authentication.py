import os
import warnings

import requests

from . import __version__
from .graphql_client import GraphQLClient
from .mutations.user import signin

warnings.filterwarnings("default", module='kili', category=DeprecationWarning)

MAX_RETRIES = 20


def get_version_without_patch(version):
    return '.'.join(version.split('.')[:-1])


class KiliAuth(object):
    """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth(email=email, password=password)
    playground = Playground(kauth)
    assets = playground.assets(project_id=project_id)
    """

    def __init__(self,
                 email=os.getenv('KILI_USER_EMAIL'),
                 password=os.getenv('KILI_USER_PASSWORD'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/graphql',
                 api_key=None,
                 verify=True):
        self.session = requests.Session()

        self.verify = verify

        self.check_versions_match(api_endpoint)

        adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.client = GraphQLClient(
            api_endpoint, self.session, verify=self.verify)
        self.client.inject_token('X-API-Key: ' + api_key)

    def __del__(self):
        self.session.close()

    def check_versions_match(self, api_endpoint):
        url = api_endpoint.replace('/graphql', '/version')
        response = requests.get(url, verify=self.verify).json()
        version = response['version']
        if get_version_without_patch(version) != get_version_without_patch(__version__):
            message = 'Kili Playground version should match with Kili API version.\n' + \
                      f'Please install version: "pip install kili=={version}"'
            warnings.warn(message, UserWarning)
