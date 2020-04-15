import warnings

from ...helpers import format_result
from .queries import GQL_USERS


def get_user(client, email: str):
    message = """This function is deprecated.
    To get users, use:
        playground.users(email=email, organization_id=organization_id)
    """
    warnings.warn(message, DeprecationWarning)


def users(client, email=None, organization_id=None):
    variables = {
        'where': {
            'email': email,
            'organizationID': organization_id
        }
    }
    result = client.execute(GQL_USERS, variables)
    return format_result('data', result)
