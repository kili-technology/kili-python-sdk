"""Module with base class for use cases."""

from abc import ABC

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway


class BaseUseCases(ABC):
    """Base Use Cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        """Initialize Base Use Cases."""
        self._kili_api_gateway = kili_api_gateway
