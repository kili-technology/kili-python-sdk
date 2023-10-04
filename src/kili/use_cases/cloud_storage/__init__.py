"""Cloud storage use cases."""
from datetime import datetime
from typing import Dict, Generator, Iterable, List, Optional

from kili.adapters.kili_api_gateway.cloud_storage.types import (
    AddDataConnectionKiliAPIGatewayInput,
)
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataIntegrationFilters,
    DataIntegrationId,
    ProjectId,
)
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

    def list_data_integrations(
        self,
        data_integration_filters: DataIntegrationFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """List data integrations."""
        return self._kili_api_gateway.list_data_integrations(
            data_integration_filters=data_integration_filters, fields=fields, options=options
        )

    def count_data_integrations(self, data_integration_filters: DataIntegrationFilters) -> int:
        """Count data integrations."""
        return self._kili_api_gateway.count_data_integrations(data_integration_filters)

    def add_data_connection(
        self,
        data_integration_id: DataIntegrationId,
        project_id: ProjectId,
        selected_folders: Optional[List[str]],
        fields: ListOrTuple[str],
    ) -> Dict:
        return self._kili_api_gateway.add_data_connection(
            fields=fields,
            data=AddDataConnectionKiliAPIGatewayInput(
                is_checking=False,
                integration_id=data_integration_id,
                last_checked=datetime.now(),
                project_id=project_id,
                selected_folders=selected_folders,
            ),
        )
