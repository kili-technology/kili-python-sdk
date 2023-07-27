"""Data integration queries."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.data_integration.queries import (
    DataIntegrationsQuery,
    DataIntegrationWhere,
)
from kili.core.helpers import disable_tqdm_if_as_generator
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesDataIntegration(BaseOperationEntrypointMixin):
    """Set of cloud storage integration queries."""

    # pylint: disable=too-many-arguments,dangerous-default-value

    @overload
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[Literal["AWS", "Azure", "GCP"]] = None,
        status: Optional[Literal["CONNECTED", "DISCONNECTED", "CHECKING"]] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["name", "id", "platform", "status"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[Literal["AWS", "Azure", "GCP"]] = None,
        status: Optional[Literal["CONNECTED", "DISCONNECTED", "CHECKING"]] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["name", "id", "platform", "status"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[Literal["AWS", "Azure", "GCP"]] = None,
        status: Optional[Literal["CONNECTED", "DISCONNECTED", "CHECKING"]] = None,
        organization_id: Optional[str] = None,
        fields: List[str] = ["name", "id", "platform", "status"],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
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
        where = DataIntegrationWhere(
            data_integration_id=cloud_storage_integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        data_integrations_gen = DataIntegrationsQuery(self.graphql_client, self.http_client)(
            where, fields, options
        )

        if as_generator:
            return data_integrations_gen
        return list(data_integrations_gen)

    @typechecked
    def count_cloud_storage_integrations(
        self,
        cloud_storage_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[Literal["AWS", "Azure", "GCP"]] = None,
        status: Optional[Literal["CONNECTED", "DISCONNECTED", "CHECKING"]] = None,
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
        where = DataIntegrationWhere(
            data_integration_id=cloud_storage_integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
        )
        return DataIntegrationsQuery(self.graphql_client, self.http_client).count(where)
