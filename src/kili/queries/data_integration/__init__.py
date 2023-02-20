"""Data integration queries."""

from typing import Dict, Iterable, List, Optional

from typeguard import typechecked
from typing_extensions import Literal

from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.data_integration.queries import (
    DataIntegrationQuery,
    DataIntegrationWhere,
)
from kili.helpers import disable_tqdm_if_as_generator


class QueriesDataIntegration:
    """
    Set of data integration queries
    """

    # pylint: disable=too-many-arguments,dangerous-default-value

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @typechecked
    def data_integrations(
        self,
        data_integration_id: Optional[str] = None,
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
        """Get a generator or a list of data integretations that match a set of criteria.

        Args:
            data_integration_id: ID of the data integration.
            name: Name of the data integration.
            platform: Platform of the data integration.
            status: Status of the data integration.
            organization_id: ID of the organization.
            fields: All the fields to request among the possible fields for the data integrations.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#dataintegration) for all possible fields.
            first: Maximum number of data integrations to return.
            skip: Number of skipped data integrations.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the data integrations is returned.

        Returns:
            A list or a generator of the data integrations that match the criteria.

        Examples:
            >>> kili.data_integrations()
            [{'name': 'My bucket', 'id': '123456789', 'platform': 'AWS', 'status': 'CONNECTED'}]
        """
        where = DataIntegrationWhere(
            data_integration_id=data_integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        data_integrations_gen = DataIntegrationQuery(self.auth.client)(where, fields, options)

        if as_generator:
            return data_integrations_gen
        return list(data_integrations_gen)

    @typechecked
    def count_data_integrations(
        self,
        data_integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[Literal["AWS", "Azure", "GCP"]] = None,
        status: Optional[Literal["CONNECTED", "DISCONNECTED", "CHECKING"]] = None,
        organization_id: Optional[str] = None,
    ) -> int:
        """Count and return the number of data integrations that match a set of criteria.

        Args:
            data_integration_id: ID of the data integration.
            name: Name of the data integration.
            platform: Platform of the data integration.
            status: Status of the data integration.
            organization_id: ID of the organization.

        Returns:
            The number of data integrations that match the criteria.
        """
        where = DataIntegrationWhere(
            data_integration_id=data_integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
        )
        return DataIntegrationQuery(self.auth.client).count(where)
