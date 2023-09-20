"""Base class for all use cases."""

from kili.adapters.kili_api_gateway import KiliAPIGateway


class BaseUseCases:
    """Base class for all use cases."""

    kili_api_gateway: KiliAPIGateway

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self.kili_api_gateway = kili_api_gateway
