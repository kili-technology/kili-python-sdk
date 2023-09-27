"""Api Keys use cases."""
import warnings
from datetime import datetime, timedelta
from typing import Generator, Optional

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.api_key import ApiKeyFilters
from kili.domain.types import ListOrTuple


class ApiKeyUseCases:
    """Api Keys use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway) -> None:
        """Init AssetUseCases."""
        self._kili_api_gateway = kili_api_gateway

    # pylint: disable=too-many-arguments
    def list_api_keys(
        self,
        filters: ApiKeyFilters,
        fields: ListOrTuple[str],
        first: Optional[int],
        skip: int,
        disable_tqdm: Optional[bool],
    ) -> Generator:
        """List api keys with given options."""
        options = QueryOptions(skip=skip, first=first, disable_tqdm=disable_tqdm)
        return self._kili_api_gateway.list_api_keys(filters, fields, options)

    def count_api_keys(self, filters: ApiKeyFilters) -> int:
        """Count api keys with given options."""
        return self._kili_api_gateway.count_api_keys(filters)

    def check_expiry_of_key_is_close(self, api_key: str) -> None:
        """Check that the expiration date of the api_key is not too close."""
        warn_days = 30

        key_expiry = self._kili_api_gateway.get_api_key_expiry_date(api_key)
        key_remaining_time = key_expiry - datetime.now()
        key_soon_deprecated = key_remaining_time < timedelta(days=warn_days)
        if key_soon_deprecated:
            message = f"""
                Your api key will be deprecated on {key_expiry:%Y-%m-%d}.
                You should generate a new one on My account > API KEY."""
            warnings.warn(message, UserWarning, stacklevel=2)

    def is_api_key_valid(self, api_key: str) -> bool:
        """Check that the api_key provided is valid."""
        return self._kili_api_gateway.is_api_key_valid(api_key)
