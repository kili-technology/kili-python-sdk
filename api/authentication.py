import os

from graphqlclient import GraphQLClient

from .mutations.user import signin


def authenticate(email, password=os.getenv('KILI_USER_PASSWORD')):
    client = GraphQLClient('https://cloud.kili-technology.com/api/label/graphql')
    auth_payload = signin(client, email, password)
    api_token = auth_payload['token']
    client.inject_token('Bearer: ' + api_token)
    user_id = auth_payload['user']['id']
    return client, user_id
