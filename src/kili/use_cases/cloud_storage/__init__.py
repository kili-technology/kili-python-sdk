"""Cloud storage use cases."""
import time
from datetime import datetime
from typing import Dict, Generator, List, Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_exponential

from kili.adapters.kili_api_gateway.cloud_storage.types import (
    AddDataConnectionKiliAPIGatewayInput,
    DataConnectionComputeDifferencesKiliAPIGatewayInput,
)
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import AssetFilters
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataDifferenceType,
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
    ) -> Generator[Dict, None, None]:
        """List data connections."""
        return self._kili_api_gateway.list_data_connections(
            data_connection_filters=data_connection_filters, fields=fields, options=options
        )

    def get_data_connection(
        self, data_connection_id: DataConnectionId, fields: ListOrTuple[str]
    ) -> Dict:
        """Get data connection."""
        return self._kili_api_gateway.get_data_connection(
            data_connection_id=data_connection_id, fields=fields
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
        """Add data connection to a project."""
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

    def compute_differences(
        self,
        data_connection_id: DataConnectionId,
        wait_until_done: bool,
    ) -> None:
        """Compute differences for a data connection."""
        data_connection = self._kili_api_gateway.get_data_connection(
            data_connection_id,
            fields=(
                "dataIntegration.azureIsUsingServiceCredentials",
                "dataIntegration.platform",
                "dataIntegration.azureSASToken",
                "dataIntegration.azureConnectionURL",
                "dataIntegration.id",
                "selectedFolders",
                "projectId",
                "isChecking",
            ),
        )
        data_integration = data_connection["dataIntegration"]
        project_id = data_connection["projectId"]

        if data_connection["isChecking"]:
            raise ValueError(
                f"Cannot compute differences for data connection {data_connection_id}."
                " Data connection is currently checking."
            )

        blob_paths = warnings = None

        # for azure using credentials, it is required to provide the blob paths to compute the diffs
        if (
            data_integration["platform"] == "Azure"
            and data_integration["azureIsUsingServiceCredentials"]
        ):
            if not (data_integration["azureSASToken"] and data_integration["azureConnectionURL"]):
                raise ValueError(
                    f"Cannot compute differences for data connection {data_connection_id} with data"
                    f" integration {data_integration['id']}. Need to provide \"azureSASToken\" and"
                    f' "azureConnectionURL" in data integration: {data_integration}'
                )

            try:
                # pylint: disable=import-outside-toplevel
                from .azure import AzureBucket
            except ImportError as err:
                raise ImportError(
                    "The azure-storage-blob package is required to use Azure buckets. "
                    " Run `pip install kili[azure]` to install it."
                ) from err

            project_input_type = self._kili_api_gateway.get_project(
                project_id=project_id, fields=("inputType",)
            )["inputType"]

            blob_paths, warnings = AzureBucket(
                sas_token=data_integration["azureSASToken"],
                connection_url=data_integration["azureConnectionURL"],
            ).get_blob_paths_azure_data_connection_with_service_credentials(
                data_connection["selectedFolders"], input_type=project_input_type
            )

        self._kili_api_gateway.compute_data_connection_differences(
            data_connection_id=data_connection_id,
            fields=("id",),
            data=(
                DataConnectionComputeDifferencesKiliAPIGatewayInput(
                    blob_paths=blob_paths, warnings=warnings
                )
                if blob_paths is not None and warnings is not None
                else None
            ),
        )
        time.sleep(1)  # backend needs some time to refresh the "isChecking"

        if not wait_until_done:
            return

        for attempt in Retrying(
            wait=wait_exponential(multiplier=1, min=1, max=4),
            stop=stop_after_delay(5 * 60),
            retry=retry_if_exception_type(ValueError),
            reraise=True,
        ):
            with attempt:
                data_connection = self._kili_api_gateway.get_data_connection(
                    data_connection_id, fields=("isChecking",)
                )
                if data_connection["isChecking"]:
                    raise ValueError(f"Data connection is still checking: {data_connection}")

        time.sleep(1)  # backend needs some time to refresh the "isChecking"

    def validate_data_differences(
        self,
        data_difference_type: DataDifferenceType,
        data_connection_id: DataConnectionId,
        wait_until_done: bool,
    ) -> None:
        """Validate data differences for a data connection.

        Args:
            data_difference_type: type of data difference to validate.
            data_connection_id: id of the data connection.
            wait_until_done: whether to wait until the validation is done.
        """
        data_connection = self._kili_api_gateway.get_data_connection(
            data_connection_id,
            fields=(
                "dataDifferencesSummary.added",
                "dataDifferencesSummary.removed",
                "dataDifferencesSummary.total",
                "projectId",
            ),
        )
        asset_diff: int = data_connection["dataDifferencesSummary"][
            "added" if data_difference_type == DataDifferenceType.ADD else "removed"
        ]

        filters = AssetFilters(project_id=data_connection["projectId"])
        nb_assets_before = self._kili_api_gateway.count_assets(filters)

        self._kili_api_gateway.validate_data_connection_differences(
            data_connection_id=data_connection_id,
            data_difference_type=data_difference_type,
            fields=("id",),
        )

        if not wait_until_done:
            return

        for attempt in Retrying(
            wait=wait_exponential(multiplier=1, min=1, max=4),
            stop=stop_after_delay(5 * 60),
            retry=retry_if_exception_type(ValueError),
            reraise=True,
        ):
            with attempt:
                nb_assets_after = self._kili_api_gateway.count_assets(filters)
                if abs(nb_assets_after - nb_assets_before) != asset_diff:
                    raise ValueError(
                        "Number of assets in project after validation is not correct: before:"
                        f" {nb_assets_before} assets, after: {nb_assets_after} assets,"
                        f" dataDifferencesSummary: {asset_diff}"
                    )
