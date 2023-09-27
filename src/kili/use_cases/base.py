from kili.adapters.kili_api_gateway import KiliAPIGateway


class BaseUseCases:
    """Tag use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        self._kili_api_gateway = kili_api_gateway
