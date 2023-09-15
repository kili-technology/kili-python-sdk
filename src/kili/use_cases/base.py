"""Base class for all use cases."""

from kili.adapters.kili_api_gateway import KiliAPIGateway


class BaseUseCases:
    """Base class for all use cases."""

    _kili_api_gateway: KiliAPIGateway
