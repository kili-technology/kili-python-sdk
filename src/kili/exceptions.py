"""Exceptions of the package."""


class NotFound(Exception):
    """Used when a given object is not found in Kili"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"Not found: '{self.name}'"


class AuthenticationFailed(Exception):
    """
    Used when the authentification fails
    """

    @staticmethod
    def _obfuscate(input_str: str) -> str:
        if len(input_str) >= 4:
            return "*" * (len(input_str) - 4) + input_str[-4:]
        return input_str

    def __init__(self, api_key, api_endpoint):
        if api_key is None:
            super().__init__(
                "You need to provide an API KEY to connect."
                " Visit https://docs.kili-technology.com/reference/creating-an-api-key"
            )
        else:
            super().__init__(
                f"Connection to Kili endpoint {api_endpoint} failed with API key:"
                f" {self._obfuscate(api_key)}. Check your connection and API key."
            )


class GraphQLError(Exception):
    """
    Used when the GraphQL call returns an error
    """

    def __init__(self, error, batch_number=None):
        if isinstance(error, list):
            error = error[0]
        if isinstance(error, dict) and "message" in error:
            error_msg = error["message"]
        else:
            error_msg = str(error)

        if batch_number is None:
            super().__init__(f'error: "{error_msg}"')
        else:
            super().__init__(f'error at index {100*batch_number}: {error_msg}"')


class NonExistingFieldError(ValueError):
    """Raised when querying a field that does not exist on an object"""


class MissingArgumentError(ValueError):
    """Raised when an required argument was not given by the user"""


class IncompatibleArgumentsError(ValueError):
    """Raised when the user gave at least two incompatible arguments"""
