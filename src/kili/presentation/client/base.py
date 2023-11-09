"""Base class for all client methods classes."""

from abc import ABC

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway


class BaseClientMethods(ABC):
    """Base class for all client methods classes.

    It is used to share the KiliAPIGateway between all client methods classes.

    It is not meant to be used and instantiated directly.
    """

    kili_api_gateway: KiliAPIGateway  # instantiated in the Kili client child class
