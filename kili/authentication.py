import os
import warnings

import requests

from . import __version__
from .graphql_client import GraphQLClient
from .playground import Playground

MAX_RETRIES = 20

warnings.filterwarnings("default", module='kili', category=DeprecationWarning)


def get_version_without_patch(version):
    return '.'.join(version.split('.')[:-1])


class KiliAuth(object):
    """
    from kili.authentication import KiliAuth
    from kili.playground import Playground
    kauth = KiliAuth(api_key=api_key)
    playground = Playground(kauth)
    assets = playground.assets(project_id=project_id)
    """

    def __init__(self,
                 api_key=os.getenv('KILI_USER_API_KEY'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/v1/graphql',
                 verify=True):
        self.session = requests.Session()

        self.verify = verify

        if api_endpoint == "https://cloud.kili-technology.com/api/label/graphql":
            message = 'We are migrating the API to enhance our service, please use the new endpoint https://cloud.kili-technology.com/api/label/v1/graphql (or None), the former endpoint call will be deprecated on october 1st 2020'
            warnings.warn(message, DeprecationWarning)
        try:
            self.check_versions_match(api_endpoint)
        except:
            message = 'We could not check the version, there might be a version mismatch or the app might be in deployment'
            warnings.warn(message, UserWarning)
            pass

        adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.client = GraphQLClient(
            api_endpoint, self.session, verify=self.verify)
        if api_key is None:
            message = 'You need to provide an API KEY to connect. Visit https://cloud.kili-technology.com/docs/python-graphql-api/authentication/#generate-an-api-key'
            warnings.warn(message, UserWarning)
        self.client.inject_token('X-API-Key: ' + api_key)
        playground = Playground(self)
        users = playground.users(api_key=api_key, fields=['id'])
        if len(users) == 0:
            raise Exception('No user attached to the API key was found')
        self.user_id = users[0]['id']

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
