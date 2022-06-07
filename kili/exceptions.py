"""Exceptions of the package."""


class NotFound(Exception):
    """Used when a given object is not found in Kili"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"Not found: '{self.name}'"


class EndpointCompatibilityError(Exception):
    """
    Used when a resolver is called but is not compatible with the endpoint
    """

    def __init__(self, resolver, endpoint):
        super().__init__(
            f'Resolver {resolver} is not compatible with the following endpoint : {endpoint}')


class GraphQLError(Exception):
    """
    Used when the GraphQL call returns an error
    """

    def __init__(self, mutation, error, batch_number=None):
        if batch_number is None:
            super().__init__(
                f'Mutation "{mutation}" failed with error: "{error}"')
        else:
            super().__init__(
                f'Mutation "{mutation}" failed from index {100*batch_number} with error: "{error}"')
