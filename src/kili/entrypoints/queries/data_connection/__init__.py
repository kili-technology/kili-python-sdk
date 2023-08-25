"""Data connection queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.data_connection.queries import (
    DataConnectionsQuery,
    DataConnectionsWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.services.data_connection import get_data_connection
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesDataConnection(BaseOperationEntrypointMixin):
    """Set of cloud storage connection queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
    def cloud_storage_connections(
        self,
        cloud_storage_connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
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
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
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
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
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

        # call dataConnection resolver
        if cloud_storage_connection_id is not None:
            data_connection = get_data_connection(self, cloud_storage_connection_id, fields)
            data_connection_list = [data_connection]
            if as_generator:
                return iter(data_connection_list)
            return data_connection_list

        # call dataConnections resolver
        where = DataConnectionsWhere(
            project_id=project_id, data_integration_id=cloud_storage_integration_id
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        data_connections_gen = DataConnectionsQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if as_generator:
            return data_connections_gen
        return list(data_connections_gen)
