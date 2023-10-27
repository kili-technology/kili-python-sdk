"""Client presentation methods for cloud storage."""

import logging
from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataIntegrationFilters,
    DataIntegrationId,
    DataIntegrationPlatform,
    DataIntegrationStatus,
    OrganizationId,
    ProjectId,
)
from kili.domain.types import ListOrTuple
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.cloud_storage import CloudStorageUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


@for_all_methods(log_call, exclude=["__init__"])
class CloudStorageClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on cloud storage."""

    @overload
    def cloud_storage_connections(
        self,
        cloud_storage_connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def cloud_storage_connections(
        self,
        cloud_storage_connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def cloud_storage_connections(
        self,
        cloud_storage_connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of cloud storage connections that match a set of criteria.

        Args:
            cloud_storage_connection_id: ID of the cloud storage connection.
            cloud_storage_integration_id: ID of the cloud storage integration.
            project_id: ID of the project.
            fields: All the fields to request among the possible fields for the cloud storage connections.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#dataconnection) for all possible fields.
            first: Maximum number of cloud storage connections to return.
            skip: Number of skipped cloud storage connections.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the cloud storage connections is returned.

        Returns:
            A list or a generator of the cloud storage connections that match the criteria.

        Examples:
            >>> kili.cloud_storage_connections(project_id="789465123")
            [{'id': '123456789', 'lastChecked': '2023-02-21T14:49:35.606Z', 'numberOfAssets': 42, 'selectedFolders': ['folder1', 'folder2'], 'projectId': '789465123'}]
        """
        if (
            cloud_storage_connection_id is None
            and cloud_storage_integration_id is None
            and project_id is None
        ):
            raise ValueError(
                "At least one of cloud_storage_connection_id, cloud_storage_integration_id or"
                " project_id must be specified"
            )

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)

        cloud_storage_use_cases = CloudStorageUseCases(self.kili_api_gateway)

        if cloud_storage_connection_id is None:
            data_connections_gen = cloud_storage_use_cases.list_data_connections(
                data_connection_filters=DataConnectionFilters(
                    project_id=ProjectId(project_id) if project_id is not None else None,
                    integration_id=(
                        DataIntegrationId(cloud_storage_integration_id)
                        if cloud_storage_integration_id is not None
                        else None
                    ),
                ),
                fields=fields,
                options=QueryOptions(disable_tqdm, first, skip),
            )
        else:
            data_connections_gen = (
                i
                for i in [
                    cloud_storage_use_cases.get_data_connection(
                        DataConnectionId(cloud_storage_connection_id), fields=fields
                    )
                ]
            )

        if as_generator:
            return data_connections_gen
        return list(data_connections_gen)

    @overload
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of cloud storage integrations that match a set of criteria.

        Args:
            cloud_storage_integration_id: ID of the cloud storage integration.
            name: Name of the cloud storage integration.
            platform: Platform of the cloud storage integration.
            status: Status of the cloud storage integration.
            organization_id: ID of the organization.
            fields: All the fields to request among the possible fields for the cloud storage integrations.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#dataintegration) for all possible fields.
            first: Maximum number of cloud storage integrations to return.
            skip: Number of skipped cloud storage integrations.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the cloud storage integrations is returned.

        Returns:
            A list or a generator of the cloud storage integrations that match the criteria.

        Examples:
            >>> kili.cloud_storage_integrations()
            [{'name': 'My bucket', 'id': '123456789', 'platform': 'AWS', 'status': 'CONNECTED'}]
        """
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        data_integrations_gen = CloudStorageUseCases(self.kili_api_gateway).list_data_integrations(
            data_integration_filters=DataIntegrationFilters(
                status=status,
                id=(
                    DataIntegrationId(cloud_storage_integration_id)
                    if cloud_storage_integration_id is not None
                    else None
                ),
                name=name,
                platform=platform,
                organization_id=(
                    OrganizationId(organization_id) if organization_id is not None else None
                ),
            ),
            fields=fields,
            options=options,
        )

        if as_generator:
            return data_integrations_gen
        return list(data_integrations_gen)

    @typechecked
    def count_cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
    ) -> int:
        """Count and return the number of cloud storage integrations that match a set of criteria.

        Args:
            cloud_storage_integration_id: ID of the cloud storage integration.
            name: Name of the cloud storage integration.
            platform: Platform of the cloud storage integration.
            status: Status of the cloud storage integration.
            organization_id: ID of the organization.

        Returns:
            The number of cloud storage integrations that match the criteria.
        """
        return CloudStorageUseCases(self.kili_api_gateway).count_data_integrations(
            DataIntegrationFilters(
                status=status,
                id=(
                    DataIntegrationId(cloud_storage_integration_id)
                    if cloud_storage_integration_id is not None
                    else None
                ),
                name=name,
                platform=platform,
                organization_id=(
                    OrganizationId(organization_id) if organization_id is not None else None
                ),
            )
        )

    @typechecked
    def add_cloud_storage_connection(
        self,
        project_id: str,
        cloud_storage_integration_id: str,
        selected_folders: Optional[List[str]] = None,
    ) -> Dict:
        """Connect a cloud storage to a project.

        Args:
            project_id: Id of the project.
            cloud_storage_integration_id: Id of the cloud storage integration.
            selected_folders: List of folders of the data integration to connect to the project.
                If not provided, all folders of the data integration will be connected.

        Returns:
            A dict with the DataConnection Id.
        """
        data_connection_id = CloudStorageUseCases(self.kili_api_gateway).add_data_connection(
            project_id=ProjectId(project_id),
            data_integration_id=DataIntegrationId(cloud_storage_integration_id),
            selected_folders=selected_folders,
            fields=("id",),
        )["id"]

        return {"id": data_connection_id}

    @typechecked
    def synchronize_cloud_storage_connection(
        self,
        cloud_storage_connection_id: str,
        delete_extraneous_files: bool = False,
        dry_run: bool = False,
    ) -> Dict:
        """Synchronize a cloud storage connection.

        This method will compute differences between the cloud storage connection and the project,
            and then validate the differences.

        If `delete_extraneous_files` is True, it will also delete files that are not in the
            cloud storage integration anymore but that are still in the project.

        Args:
            cloud_storage_connection_id: Id of the cloud storage connection.
            delete_extraneous_files: If True, delete extraneous files.
            dry_run: If True, will not synchronize the data connection but only print the
                differences. This is useful to check the differences before applying them to the
                project.

        Returns:
            A dict with the cloud storage connection Id.
        """
        data_connection_id = DataConnectionId(cloud_storage_connection_id)

        cloud_storage_use_cases = CloudStorageUseCases(self.kili_api_gateway)

        cloud_storage_use_cases.synchronize_data_connection(
            data_connection_id=data_connection_id,
            delete_extraneous_files=delete_extraneous_files,
            dry_run=dry_run,
            logger=logger,
        )

        return cloud_storage_use_cases.get_data_connection(
            data_connection_id=data_connection_id, fields=("numberOfAssets", "projectId")
        )
