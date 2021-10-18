"""
Api key mutations
"""

from typeguard import typechecked
from ...helpers import Compatible, deprecate, format_result

from .queries import GQL_APPEND_TO_API_KEYS

class MutationsApiKey: # pylint: disable=too-few-public-methods
    """
    Set of User mutations
    """
    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    @typechecked
    def append_to_api_keys(self, api_key: str, name: str):
        """
        Create an api key to connect to the API

        Parameters
        ----------
        - api_key : str, a new api key to connect with
        - name : str, a name used to describe the api key.
        """
        variables = {
            'data': {'key': api_key,
                     'name': name},
            'where': {'email': self.auth.user_email}
        }
        result = self.auth.client.execute(GQL_APPEND_TO_API_KEYS, variables)
        return format_result('data', result)
