"""Abstract class for use cases."""
from kili.adapters.kili_api_gateway import KiliAPIGateway


class AbstractUseCases:
    """Abstract class for use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self._kili_api_gateway = kili_api_gateway
