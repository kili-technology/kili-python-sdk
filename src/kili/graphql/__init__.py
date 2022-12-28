"""
GraphQL module
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Type

from tqdm import tqdm

from kili.helpers import format_result, fragment_builder
from kili.utils.pagination import api_throttle

from ..graphql_client import GraphQLClient


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK"""

    first: Optional[int] = None
    skip: int = 0
    disable_tqdm: bool = True
    as_generator: bool = False


class GraphQLQuery(ABC):
    """
    Query class for querying Kili objects.
    It factorizes code for executing paginated queries
    """

    def __init__(
        self,
        client: GraphQLClient,
    ):
        self.client = client
        self.default_options = QueryOptions()

    @staticmethod
    @abstractmethod
    def query(fragment: str) -> str:
        """Return the GraphQL object query to be sent, according to the fragment to return.

        Args:
            fragment: the fragment to return in the query

        Return:
            The query to be sent to graphQL
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def where_payload_builder(where) -> Dict:
        """Build the where payload to be sent to graphQL to restrict the query.
        It takes the SDK flatten Where as input and
        convert it into the right where needed to call the resolver
        """
        raise NotImplementedError

    COUNT_QUERY: str = NotImplemented

    TYPE: Type = NotImplemented

    # to be implemented when adding the asset query with the new architecture
    # @staticmethod
    # @abstractmethod
    # def post_call_process():

    def __call__(
        self,
        where,
        fields: List[str],
        options: Optional[QueryOptions] = None,
    ) -> Iterable[Dict]:
        """Query objects of the specified type"""
        options = options or self.default_options
        fragment = fragment_builder(fields, self.TYPE)
        where_payload = self.where_payload_builder(where)
        query = self.query(fragment)

        result_gen = self.execute_query_from_paginated_call(query, where_payload, options)
        if options.as_generator:
            return result_gen
        return list(result_gen)

    def count(self, where_payload):
        """Count the number of objects matching the given where payload"""
        payload = {"where": where_payload}
        count_result = self.client.execute(self.COUNT_QUERY, payload)
        return format_result("data", count_result, int)

    def get_number_of_elements_to_query(self, where_payload: Dict, options):
        """Return the total number of element to query for one query.
        It uses both the argument first given by the user
        and the total number of available objects obtained with a graphQL count query
        """
        first = options.first
        if not options.disable_tqdm:
            count_rows_available = self.count(where_payload)
            if first is None:
                return count_rows_available
            return min(count_rows_available, first)
        # dummy value that won't have any impact since tqdm is disabled
        return 1 if first != 0 else 0

    def execute_query_from_paginated_call(
        self, query: str, where_payload: Dict, options: QueryOptions
    ):
        """
        Builds a row generator from paginated calls.

        Args:
            skip: Number of assets to skip
                (they are ordered by their date of creation, first to last).
            first: Maximum number of assets to return.
            count_method: Callable returning the number of available assets given `count_args`.
            count_kwargs: Keyword arguments passed to the `count_method`.
            paged_call_method: Callable returning the list of samples.
            paged_call_payload: Payload for the GraphQL query.
            fields: The list of strings to retrieved.
            disable_tqdm: If `True`, disables tqdm.
        """
        payload: Dict[str, Any] = {"where": where_payload}
        if options.as_generator and not options.disable_tqdm:
            options._replace(disable_tqdm=True)
        total_rows_queried = self.get_number_of_elements_to_query(where_payload, options)
        count_rows_query_per_call = min(100, options.first or 100)

        if total_rows_queried == 0:
            yield from ()
        else:
            with tqdm(total=total_rows_queried, disable=options.disable_tqdm) as pbar:
                count_rows_retrieved = 0
                while True:
                    skip = count_rows_retrieved + options.skip
                    payload.update({"skip": skip, "first": count_rows_query_per_call})
                    rows = api_throttle(self.client.execute)(query, payload)
                    rows = format_result("data", rows)

                    if rows is None or len(rows) == 0:
                        break

                    # to be implemented when adding the asset query with the new architecture
                    # if self.post_call_process is not None:
                    #     rows = self.post_call_process(rows)

                    for row in rows:
                        yield row

                    count_rows_retrieved += len(rows)
                    pbar.update(len(rows))
                    if options.first is not None and count_rows_retrieved >= options.first:
                        break
