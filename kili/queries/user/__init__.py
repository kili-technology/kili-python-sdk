from ...helpers import format_result
from .queries import GQL_GET_USER


def get_user(client, email: str):
    variables = {'email': email}
    result = client.execute(GQL_GET_USER, variables)
    return format_result('data', result)
