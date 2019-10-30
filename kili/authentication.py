import os
import requests

from .graphql_client import GraphQLClient

from .mutations.user import signin

MAX_RETRIES = 20


def authenticate(email,
                 password=os.getenv('KILI_USER_PASSWORD'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/graphql'):

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
