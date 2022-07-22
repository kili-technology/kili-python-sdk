"""Exceptions of the package."""
import ast


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

    def __init__(self, api_key, api_endpoint):
        if api_key is None:
            super().__init__(
                "You need to provide an API KEY to connect."
                " Visit https://docs.kili-technology.com/reference/creating-an-api-key"
            )
        else:
            super().__init__(
                f"Connection to Kili endpoint {api_endpoint} failed with API key: {api_key}."
                " Check your connection and API key."
            )


class EndpointCompatibilityError(Exception):
    """
    Used when a resolver is called but is not compatible with the endpoint
    """

    def __init__(self, resolver, endpoint):
        super().__init__(
            f"Resolver {resolver} is not compatible with the following endpoint : {endpoint}"
        )


class GraphQLError(Exception):
    """
    Used when the GraphQL call returns an error
    """

    def __init__(self, error: Exception, batch_number=None):
        if batch_number is None:
            super().__init__(f'error: "{ast.literal_eval(str(error))[0]["message"]}"')
        else:
            super().__init__(
                f"error at index {100*batch_number}: "
                f'{ast.literal_eval(str(error))[0]["message"]}"'
            )
