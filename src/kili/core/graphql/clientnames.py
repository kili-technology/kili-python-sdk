"""Client names."""

from enum import Enum


class GraphQLClientName(Enum):
    """GraphQL client name."""

    SDK = "python-sdk"
    SDK_DOMAIN = "python-sdk-domain"
    CLI = "python-cli"
