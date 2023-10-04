"""Client presentation methods for cloud storage."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataIntegrationId,
    ProjectId,
)
from kili.domain.types import ListOrTuple
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.cloud_storage import CloudStorageUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


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
    ) -> Generator[Dict, None, None]: ...

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
    ) -> List[Dict]: ...

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

        data_connections_gen = CloudStorageUseCases(self.kili_api_gateway).list_data_connections(
            data_connection_filters=DataConnectionFilters(
                data_connection_id=(
                    DataConnectionId(cloud_storage_connection_id)
                    if cloud_storage_connection_id is not None
                    else None
                ),
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

        if as_generator:
            return data_connections_gen
        return list(data_connections_gen)
