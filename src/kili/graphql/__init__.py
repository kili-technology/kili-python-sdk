"""
GraphQL module
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Generator, List, NamedTuple, Optional, Type, Union

from tqdm import tqdm
from typeguard import typechecked

from kili.constants import QUERY_BATCH_SIZE
from kili.helpers import format_result
from kili.utils.pagination import api_throttle

from .graphql_client import GraphQLClient


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK"""

    disable_tqdm: Optional[bool]
    first: Optional[int] = None
    skip: int = 0


class BaseQueryWhere(ABC):
    """
    Abtsract class for defining the where payload to send in a graphQL query
    """

    def __init__(self):
        self._graphql_payload = self.graphql_where_builder()

    @abstractmethod
    def graphql_where_builder(self) -> Dict:
        """Build the GraphQL where payload sent in the resolver from the
        arguments given to the where class
        """
        raise NotImplementedError

    @property
    def graphql_payload(self):
        """where payload to send in the graphQL query"""
        return self._graphql_payload


class GraphQLQuery(ABC):
    """
    Query class for querying Kili objects.
    It factorizes code for executing paginated queries
    """

    def __init__(
        self,
        client: GraphQLClient,
        ssl_verify: Union[bool, str],
    ) -> None:
        self.client = client
        self.ssl_verify = ssl_verify

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

    COUNT_QUERY: str = NotImplemented
    FORMAT_TYPE: Optional[Type] = None

    def __call__(
        self,
        where: BaseQueryWhere,
        fields: List[str],
        options: QueryOptions,
        post_call_function: Optional[Callable] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of objects of the specified type in accordance with the provided where"""
        fragment = self.fragment_builder(fields)
        query = self.query(fragment)

        return self.execute_query_from_paginated_call(query, where, options, post_call_function)

    def count(self, where: BaseQueryWhere) -> int:
        """Count the number of objects matching the given where payload"""
        payload = {"where": where.graphql_payload}
        count_result = self.client.execute(self.COUNT_QUERY, payload)
        return format_result("data", count_result, int, self.ssl_verify)

    def get_number_of_elements_to_query(self, where: BaseQueryWhere, options: QueryOptions):
        """Return the total number of element to query for one query.
        It uses both the argument first given by the user
        and the total number of available objects obtained with a graphQL count query
        """
        first = options.first
        skip = options.skip
        count_rows_available = self.count(where)
        count_objects_queried = max(count_rows_available - skip, 0)
        if first is None:
            return count_objects_queried
        return min(count_objects_queried, first)

    def execute_query_from_paginated_call(
        self,
        query: str,
        where: BaseQueryWhere,
        options: QueryOptions,
        post_call_function: Optional[Callable],
    ) -> Generator[Dict, None, None]:
        """
        Builds a row generator from paginated calls.

        Args:
            query: The object query to execute and to send to graphQL, in string format
            where_payload: The where payload to be sent to graphQL,
                as a value of the 'where' key in the global payload
            options: The query options
        """
        # we can get the total number of elements to query
        if isinstance(self.COUNT_QUERY, str):
            nb_rows_to_query = self.get_number_of_elements_to_query(where, options)
            disable_tqdm = options.disable_tqdm

        # we don't have count methods but we know the total number of elements to query
        elif options.first is not None:
            nb_rows_to_query = options.first
            disable_tqdm = options.disable_tqdm

        # we don't have count methods and we don't know the total number of elements to query
        else:
            nb_rows_to_query = None
            disable_tqdm = True

        if nb_rows_to_query == 0:
            yield from ()
        else:
            with tqdm(total=nb_rows_to_query, disable=disable_tqdm) as pbar:
                count_rows_retrieved = 0
                while True:
                    if nb_rows_to_query is not None and count_rows_retrieved >= nb_rows_to_query:
                        break

                    skip = count_rows_retrieved + options.skip
                    first = (
                        min(QUERY_BATCH_SIZE, nb_rows_to_query - count_rows_retrieved)
                        if nb_rows_to_query is not None
                        else QUERY_BATCH_SIZE
                    )
                    payload = {"where": where.graphql_payload, "skip": skip, "first": first}
                    rows = api_throttle(self.client.execute)(query, payload)
                    rows = format_result("data", rows, self.FORMAT_TYPE, self.ssl_verify)

                    if rows is None or len(rows) == 0:
                        break

                    if post_call_function is not None:
                        rows = post_call_function(rows)

                    if isinstance(rows, Dict):
                        yield rows
                        break

                    for row in rows:
                        yield row

                    count_rows_retrieved += len(rows)
                    pbar.update(len(rows))

                    if len(rows) < first:
                        break

    @typechecked
    def fragment_builder(self, fields: List[str]):
        """
        Builds a GraphQL fragment for a list of fields to query

        Args:
            fields: The list of fields to query
        """
        fragment = ""

        # split a field and its subfields (e.g. "roles.user.id" -> ["roles", "user.id"])
        subfields = [field.split(".", 1) for field in fields if "." in field]

        if subfields:
            # get the root fields (e.g. "roles" in "roles.user.id")
            root_fields = {subfield[0] for subfield in subfields}
            for root_field in root_fields:
                # get the subfields of the root field (e.g. "user.id" in "roles.user.id")
                fields_subquery = [
                    subfield[1] for subfield in subfields if subfield[0] == root_field
                ]
                # build the subquery fragment (e.g. "user{id}" in "roles{user{id}}")
                new_fragment = self.fragment_builder(fields_subquery)
                # add the subquery to the fragment
                fragment += f" {root_field}{{{new_fragment}}}"

            # remove the fields that have been queried in subqueries (e.g. "roles.user.id")
            fields = [field for field in fields if "." not in field]

        for field in fields:
            fragment += f" {field}"

        return fragment
