"""Cloud storage use cases."""
from typing import Dict, Iterable

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.cloud_storage import DataConnectionFilters
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases


class CloudStorageUseCases(BaseUseCases):
    """CloudStorage use cases."""

    def list_data_connections(
        self,
        data_connection_filters: DataConnectionFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Iterable[Dict]:
        """List data connections."""
        if data_connection_filters.data_connection_id is None:
            return self._kili_api_gateway.list_data_connections(
                data_connection_filters=data_connection_filters, fields=fields, options=options
            )

        return iter(
            [
                self._kili_api_gateway.get_data_connection(
                    data_connection_id=data_connection_filters.data_connection_id, fields=fields
                )
            ]
        )
