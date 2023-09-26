"""Base class for all use cases."""

import abc
from kili.adapters.kili_api_gateway import KiliAPIGateway


class BaseUseCases(abc.ABC):
    """Base class for all use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self.kili_api_gateway = kili_api_gateway
