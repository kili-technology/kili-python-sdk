import os

from graphqlclient import GraphQLClient

from .mutations.user import signin


def authenticate(email,
                 password=os.getenv('KILI_USER_PASSWORD'),
                 api_endpoint='http://localhost:4000/graphql'):
    client = GraphQLClient(api_endpoint)
    auth_payload = signin(client, email, password)
    api_token = auth_payload['token']
    client.inject_token('Bearer: ' + api_token)
    user_id = auth_payload['user']['id']
    return client, user_id
