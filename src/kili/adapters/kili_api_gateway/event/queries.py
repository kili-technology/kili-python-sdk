"""GraphQL module."""

from typing import Any, Dict, Generator

from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.event import QueryOptions


class PaginatedGraphQLQuery:
    """Query class for querying Kili objects.

    It factorizes code for executing paginated queries.
    """

    def __init__(self, graphql_client: GraphQLClient) -> None:
        """Initialize the paginator."""
        self._graphql_client = graphql_client

    def execute_query_from_paginated_call(
        self,
        query: str,
        where: Dict[str, Any],
        pagination: Dict[str, Any],
        options: QueryOptions,
    ) -> Generator[Dict, None, None]:
        """Build a row generator from paginated query calls with the first and skip pattern.

        Args:
            query: The object query to execute and to send to graphQL, in string format
            where: The where payload to send in the graphQL query
            pagination: The where pagination payload to send in the graphQL query
            options: The query options with skip and first and disable_tqdm
        """
        count_elements_retrieved = 0
        while True:
            skip = count_elements_retrieved + options.skip
            first = options.batch_size
            order = options.order

            payload = {
                "where": where,
                "pagination": {"skip": skip, "first": first, **pagination},
                "order": order,
            }
            elements = self._graphql_client.execute(query, payload)["data"]
            if not isinstance(elements, list):
                raise TypeError(
                    "PaginatedGraphQLQuery only support operations returning a list of objects"
                )

            if len(elements) == 0:
                break

            yield from elements

            count_elements_retrieved += len(elements)

            if len(elements) < first:
                break
