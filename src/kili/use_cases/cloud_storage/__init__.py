"""Cloud storage use cases."""

import logging
import time
from datetime import datetime
from logging import Logger
from typing import Dict, Generator, List, Optional

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_exponential

from kili.adapters.kili_api_gateway.cloud_storage.mappers import integration_data_mapper
from kili.adapters.kili_api_gateway.cloud_storage.types import (
    AddDataConnectionKiliAPIGatewayInput,
    DataConnectionComputeDifferencesKiliAPIGatewayInput,
    DataIntegrationData,
)
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetFilters
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataDifferenceType,
    DataIntegrationFilters,
    DataIntegrationId,
    DataIntegrationPlatform,
    DataIntegrationStatus,
    ProjectId,
)
from kili.domain.organization import OrganizationId
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
        if (
            self._kili_api_gateway.count_data_integrations(
                DataIntegrationFilters(id=data_integration_id)
            )
            == 0
        ):
            raise ValueError(f"Cloud storage integration with id {data_integration_id} not found.")
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

    def synchronize_data_connection(
        self,
        data_connection_id: DataConnectionId,
        delete_extraneous_files: bool,
        dry_run: bool,
        logger: Optional[Logger],
    ) -> None:
        """Synchronize data connection."""
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.addHandler(logging.NullHandler())

        logger.info("Synchronizing data connection: %s", data_connection_id)

        _compute_differences(data_connection_id, self._kili_api_gateway)

        data_connection = self._kili_api_gateway.get_data_connection(
            data_connection_id,
            fields=(
                "id",
                "dataDifferencesSummary.added",
                "dataDifferencesSummary.removed",
                "dataDifferencesSummary.total",
                "isChecking",
                "numberOfAssets",
                "projectId",
            ),
        )
        if data_connection["isChecking"]:
            raise ValueError(f"Data connection should not be checking: {data_connection}")

        added = data_connection["dataDifferencesSummary"]["added"]
        removed = data_connection["dataDifferencesSummary"]["removed"]
        total = data_connection["dataDifferencesSummary"]["total"]
        nb_assets = data_connection["numberOfAssets"]

        logger.info("Currently %d asset(s) imported from the data connection.", nb_assets)

        if total == 0:
            logger.info("No differences found. Nothing to synchronize.")
            return

        logger.info(
            "Found %d difference(s): %d asset(s) to add, %d asset(s) to remove.",
            total,
            added,
            removed,
        )

        if dry_run:
            # pylint: disable=unnecessary-lambda-assignment
            validate_data_differences_func = lambda *args, **kwargs: None  # noqa: ARG005
            logger.info("Dry run: no data will be added or removed.")
        else:
            validate_data_differences_func = _validate_data_differences

        if added > 0:
            validate_data_differences_func(
                data_connection_id=data_connection_id,
                data_difference_type=DataDifferenceType.ADD,
                kili_api_gateway=self._kili_api_gateway,
            )
            logger.info("Added %d file(s).", added)

        if removed > 0:
            if delete_extraneous_files:
                validate_data_differences_func(
                    data_connection_id=data_connection_id,
                    data_difference_type=DataDifferenceType.REMOVE,
                    kili_api_gateway=self._kili_api_gateway,
                )
                logger.info("Removed %d extraneous file(s).", removed)
            else:
                logger.info(
                    "Use delete_extraneous_files=True to remove %d extraneous file(s).",
                    removed,
                )

    def create_data_integration(
        self,
        allowed_paths: Optional[List[str]],
        allowed_projects: Optional[List[str]],
        aws_access_point_arn: Optional[str],
        aws_role_arn: Optional[str],
        aws_role_external_id: Optional[str],
        azure_connection_url: Optional[str],
        azure_is_using_service_credentials: Optional[bool],
        azure_sas_token: Optional[str],
        azure_tenant_id: Optional[str],
        gcp_bucket_name: Optional[str],
        include_root_files: Optional[str],
        internal_processing_authorized: Optional[str],
        name: str,
        platform: DataIntegrationPlatform,
        s3_access_key: Optional[str],
        s3_bucket_name: Optional[str],
        s3_endpoint: Optional[str],
        s3_region: Optional[str],
        s3_secret_key: Optional[str],
        s3_session_token: Optional[str],
        fields: ListOrTuple[str],
    ) -> Dict:
        """Create a data integration."""
        data = DataIntegrationData(
            allowed_paths=allowed_paths,
            allowed_projects=allowed_projects,
            aws_access_point_arn=aws_access_point_arn,
            aws_role_arn=aws_role_arn,
            aws_role_external_id=aws_role_external_id,
            azure_connection_url=azure_connection_url,
            azure_is_using_service_credentials=azure_is_using_service_credentials,
            azure_sas_token=azure_sas_token,
            azure_tenant_id=azure_tenant_id,
            gcp_bucket_name=gcp_bucket_name,
            include_root_files=include_root_files,
            internal_processing_authorized=internal_processing_authorized,
            name=name,
            organization_id=OrganizationId(""),
            platform=platform,
            status="CHECKING",
            s3_access_key=s3_access_key,
            s3_bucket_name=s3_bucket_name,
            s3_endpoint=s3_endpoint,
            s3_region=s3_region,
            s3_secret_key=s3_secret_key,
            s3_session_token=s3_session_token,
        )

        return self._kili_api_gateway.create_data_integration(fields=fields, data=data)

    def update_data_integration(
        self,
        data_integration_id: DataIntegrationId,
        allowed_paths: Optional[List[str]],
        allowed_projects: Optional[List[str]],
        aws_access_point_arn: Optional[str],
        aws_role_arn: Optional[str],
        aws_role_external_id: Optional[str],
        azure_connection_url: Optional[str],
        azure_is_using_service_credentials: Optional[bool],
        azure_sas_token: Optional[str],
        azure_tenant_id: Optional[str],
        gcp_bucket_name: Optional[str],
        include_root_files: Optional[str],
        internal_processing_authorized: Optional[str],
        name: Optional[str],
        platform: Optional[DataIntegrationPlatform],
        organization_id: Optional[str],
        s3_access_key: Optional[str],
        s3_bucket_name: Optional[str],
        s3_endpoint: Optional[str],
        s3_region: Optional[str],
        s3_secret_key: Optional[str],
        s3_session_token: Optional[str],
        status: Optional[DataIntegrationStatus],
    ) -> Dict:
        """Update data integration."""
        organization_id = OrganizationId(organization_id) if organization_id else None
        data = DataIntegrationData(
            allowed_paths=allowed_paths,
            allowed_projects=allowed_projects,
            aws_access_point_arn=aws_access_point_arn,
            aws_role_arn=aws_role_arn,
            aws_role_external_id=aws_role_external_id,
            azure_connection_url=azure_connection_url,
            azure_is_using_service_credentials=azure_is_using_service_credentials,
            azure_sas_token=azure_sas_token,
            azure_tenant_id=azure_tenant_id,
            gcp_bucket_name=gcp_bucket_name,
            include_root_files=include_root_files,
            internal_processing_authorized=internal_processing_authorized,
            name=name,
            organization_id=organization_id,
            platform=platform,
            status=status,
            s3_access_key=s3_access_key,
            s3_bucket_name=s3_bucket_name,
            s3_endpoint=s3_endpoint,
            s3_region=s3_region,
            s3_secret_key=s3_secret_key,
            s3_session_token=s3_session_token,
        )
        fields = tuple(
            name for name, val in integration_data_mapper(data).items() if val is not None
        )
        if "id" not in fields:
            fields += ("id",)

        return self._kili_api_gateway.update_data_integration(
            data_integration_id,
            data_integration_data=data,
            fields=fields,
        )

    def delete_data_integration(self, data_integration_id: DataIntegrationId) -> str:
        """Delete a data integration."""
        return self._kili_api_gateway.delete_data_integration(data_integration_id)


def _compute_differences(
    data_connection_id: DataConnectionId, kili_api_gateway: KiliAPIGateway
) -> None:
    """Compute data connection differences.

    Calls the compute_data_connection_differences mutation
    and waits until the data connection is not checking anymore.
    """
    data_connection = kili_api_gateway.get_data_connection(
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
            "exclude",
            "include",
            "prefix",
        ),
    )
    data_integration = data_connection["dataIntegration"]

    if data_connection["isChecking"]:
        raise ValueError(
            f"Cannot compute differences for data connection {data_connection_id}."
            " Data connection is already currently checking."
        )

    blob_paths = warnings = content_types = None

    # for azure using credentials, it is required to provide the blob paths to compute the diffs
    if (
        data_integration["platform"] == "Azure"
        and data_integration["azureIsUsingServiceCredentials"]
    ):
        try:
            # pylint: disable=import-outside-toplevel
            from .azure import (
                get_blob_paths_azure_data_connection_with_service_credentials,
            )
        except ImportError as err:
            raise ImportError(
                "The azure-storage-blob package is required to use Azure buckets. "
                " Run `pip install kili[azure]` to install it."
            ) from err

        project_input_type = kili_api_gateway.get_project(
            project_id=data_connection["projectId"], fields=("inputType",)
        )["inputType"]
        (
            blob_paths,
            warnings,
            content_types,
        ) = get_blob_paths_azure_data_connection_with_service_credentials(
            input_type=project_input_type,
            data_connection=data_connection,
            data_integration=data_integration,
        )

    kili_api_gateway.compute_data_connection_differences(
        data_connection_id=data_connection_id,
        fields=("id",),
        data=(
            DataConnectionComputeDifferencesKiliAPIGatewayInput(
                blob_paths=blob_paths, warnings=warnings, content_types=content_types
            )
            if blob_paths is not None and warnings is not None and content_types is not None
            else None
        ),
    )
    time.sleep(1)  # backend needs some time to refresh the "isChecking"

    for attempt in Retrying(
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_delay(5 * 60),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
    ):
        with attempt:
            data_connection = kili_api_gateway.get_data_connection(
                data_connection_id, fields=("isChecking",)
            )
            if data_connection["isChecking"]:
                raise ValueError(f"Data connection is still checking: {data_connection}")

    time.sleep(1)  # backend needs some time to refresh the "isChecking"


def _validate_data_differences(
    data_difference_type: DataDifferenceType,
    data_connection_id: DataConnectionId,
    kili_api_gateway: KiliAPIGateway,
) -> None:
    """Validate data differences for a data connection.

    Calls the validate_data_connection_differences mutation
    and waits until the number of assets in the project is correct.
    """
    data_connection = kili_api_gateway.get_data_connection(
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
    nb_assets_before = kili_api_gateway.count_assets(filters)

    kili_api_gateway.validate_data_connection_differences(
        data_connection_id=data_connection_id,
        data_difference_type=data_difference_type,
        fields=("id",),
    )

    for attempt in Retrying(
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_delay(5 * 60),
        retry=retry_if_exception_type(ValueError),
        reraise=True,
    ):
        with attempt:
            nb_assets_after = kili_api_gateway.count_assets(filters)
            if abs(nb_assets_after - nb_assets_before) != asset_diff:
                raise ValueError(
                    "Number of assets in project after validation is not correct: before:"
                    f" {nb_assets_before} assets, after: {nb_assets_after} assets,"
                    f" dataDifferencesSummary: {asset_diff}"
                )
