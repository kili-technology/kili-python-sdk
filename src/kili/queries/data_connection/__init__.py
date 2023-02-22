"""Data connection queries."""

from typing import Dict, Generator, Iterable, List, Optional, overload

from typeguard import typechecked
from typing_extensions import Literal

from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.data_connection.queries import (
    DataConnectionsQuery,
    DataConnectionsWhere,
)
from kili.helpers import disable_tqdm_if_as_generator


# pylint: disable=too-few-public-methods
class QueriesDataConnection:
    """
    Set of data connection queries
    """

    # pylint: disable=too-many-arguments,dangerous-default-value

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @overload
    def data_connections(
        self,
        project_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "isApplyingDataDifferences",
            "isChecking",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def data_connections(
        self,
        project_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "isApplyingDataDifferences",
            "isChecking",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def data_connections(
        self,
        project_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        fields: List[str] = [
            "id",
            "lastChecked",
            "numberOfAssets",
            "isApplyingDataDifferences",
            "isChecking",
        ],
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: bool = False,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of data connections that match a set of criteria.

        Args:
            project_id: ID of the project.
            integration_id: ID of the data integration.
            fields: All the fields to request among the possible fields for the data connections.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#dataconnection) for all possible fields.
            first: Maximum number of data connections to return.
            skip: Number of skipped data connections.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the data connections is returned.

        Returns:
            A list or a generator of the data connections that match the criteria.

        Examples:
            >>> kili.data_connections(project_id="789465123")
            [{'id': '123456789', 'lastChecked': '2023-02-21T14:49:35.606Z', 'numberOfAssets': 42, 'isApplyingDataDifferences': False, 'isChecking': False}]
        """
        where = DataConnectionsWhere(project_id=project_id, integration_id=integration_id)
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        data_connections_gen = DataConnectionsQuery(self.auth.client)(where, fields, options)

        if as_generator:
            return data_connections_gen
        return list(data_connections_gen)
