from typing import Any, Callable, Dict, List, NamedTuple, Optional, Type

from tqdm import tqdm

from kili.helpers import format_result, fragment_builder
from kili.utils.pagination import api_throttle

from ..graphql_client import GraphQLClient


class QueryOptions(NamedTuple):
    first: Optional[int] = None
    skip: int = 0
    disable_tqdm: bool = True
    as_generator: bool = False


class GraphQLQuery:
    def __init__(
        self,
        _type: Type,
        query: Callable,
        count_query: str,
        where_payload_builder: Callable,
        post_call_process: Optional[Callable] = None,
    ):
        self.type = _type
        self.query = query
        self.count_query = count_query
        self.where_payload_builder = where_payload_builder
        self.post_call_process = post_call_process
        self.default_options = QueryOptions()

    def __call__(
        self,
        client: GraphQLClient,
        where,
        fields: List[str],
        options: Optional[QueryOptions] = None,
    ):
        """Query objects of the specified type"""
        options = options or self.default_options
        fragment = fragment_builder(fields, self.type)
        where_payload = self.where_payload_builder(where)
        query = self.query(fragment)

        result_gen = self.execute_query_from_paginated_call(client, query, where_payload, options)
        if options.as_generator:
            return result_gen
        return list(result_gen)

    def count(self, client: GraphQLClient, where_payload):
        """Count the number of objects matching the given where payload"""
        payload = {"where": where_payload}
        count_result = client.execute(self.count_query, payload)
        return format_result("data", count_result, int)

    def get_number_of_elements_to_query(self, client: GraphQLClient, where_payload: Dict, options):
        """Return the total number of element to query for one query.
        It uses both the argument first given by the user
        and the total number of available objects obtained with a graphQL count query
        """
        first = options.first
        if not options.disable_tqdm:
            count_rows_available = self.count(client, where_payload)
            if first is None:
                return count_rows_available
            return min(count_rows_available, first)
        # dummy value that won't have any impact since tqdm is disabled
        return 1 if first != 0 else 0

    def execute_query_from_paginated_call(
        self, client: GraphQLClient, query: str, where_payload: Dict, options: QueryOptions
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
        total_rows_queried = self.get_number_of_elements_to_query(client, where_payload, options)
        count_rows_query_per_call = min(100, options.first or 100)

        if total_rows_queried == 0:
            yield from ()
        else:
            with tqdm(total=total_rows_queried, disable=options.disable_tqdm) as pbar:
                count_rows_retrieved = 0
                while True:
                    skip = count_rows_retrieved + options.skip
                    payload.update({"skip": skip, "first": count_rows_query_per_call})
                    rows = api_throttle(client.execute)(query, payload)
                    rows = format_result("data", rows)

                    if rows is None or len(rows) == 0:
                        break

                    if self.post_call_process is not None:
                        rows = self.post_call_process(rows)

                    for row in rows:
                        yield row

                    count_rows_retrieved += len(rows)
                    pbar.update(len(rows))
                    if options.first is not None and count_rows_retrieved >= options.first:
                        break
