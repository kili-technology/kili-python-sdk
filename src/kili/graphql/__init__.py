"""
GraphQL module
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Type

from tqdm import tqdm
from typing_extensions import TypedDict, is_typeddict

from kili.exceptions import NonExistingFieldError
from kili.helpers import format_result
from kili.utils.pagination import api_throttle

from .graphql_client import GraphQLClient


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK"""

    disable_tqdm: Optional[bool]
    first: Optional[int] = None
    skip: int = 0
    as_generator: bool = False


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
    ):
        self.client = client

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

    FORMAT_TYPE: Type = NotImplemented

    FRAGMENT_TYPE: Type = NotImplemented

    def __call__(
        self,
        where: BaseQueryWhere,
        fields: List[str],
        options: QueryOptions,
        post_call_function: Optional[Callable] = None,
    ) -> Iterable[Dict]:
        """Query objects of the specified type"""
        fragment = self.fragment_builder(fields, self.FRAGMENT_TYPE)
        query = self.query(fragment)

        result_gen = self.execute_query_from_paginated_call(
            query, where, options, post_call_function
        )
        if options.as_generator:
            return result_gen
        return list(result_gen)

    def count(self, where: BaseQueryWhere):
        """Count the number of objects matching the given where payload"""
        payload = {"where": where.graphql_payload}
        count_result = self.client.execute(self.COUNT_QUERY, payload)
        return format_result("data", count_result, int)

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
    ):
        """
        Builds a row generator from paginated calls.

        Args:
            query: The object query to execute and to send to graphQL, in string format
            where_payload: The where payload to be sent to graphQL,
                as a value of the 'where' key in the global payload
            options: The query options
        """
        if options.as_generator and not options.disable_tqdm:
            options._replace(disable_tqdm=True)
        total_rows_queried = self.get_number_of_elements_to_query(where, options)
        batch_size = min(100, options.first or 100)

        if total_rows_queried == 0:
            yield from ()
        else:
            with tqdm(total=total_rows_queried, disable=options.disable_tqdm) as pbar:
                count_rows_retrieved = 0
                while count_rows_retrieved < total_rows_queried:
                    skip = count_rows_retrieved + options.skip
                    payload = {"where": where.graphql_payload, "skip": skip, "first": batch_size}
                    rows = api_throttle(self.client.execute)(query, payload)
                    rows = format_result("data", rows, _object=self.FORMAT_TYPE)

                    if rows is None or len(rows) == 0:
                        break

                    if post_call_function is not None:
                        rows = post_call_function(rows)

                    for row in rows:
                        yield row

                    count_rows_retrieved += len(rows)
                    pbar.update(len(rows))

    def fragment_builder(self, fields: List[str], typed_dict_class: Type[TypedDict]):
        """
        Builds a GraphQL fragment for a list of fields to query

        Args:
            fields
            type_of_fields
        """
        type_of_fields = typed_dict_class.__annotations__
        fragment = ""
        subfields = [field.split(".", 1) for field in fields if "." in field]
        if subfields:
            for subquery in {subfield[0] for subfield in subfields}:
                type_of_fields_subquery = type_of_fields[subquery]
                if type_of_fields_subquery == str:
                    raise NonExistingFieldError(f"{subquery} field does not take subfields")
                if is_typeddict(type_of_fields_subquery):
                    fields_subquery = [
                        subfield[1] for subfield in subfields if subfield[0] == subquery
                    ]
                    new_fragment = self.fragment_builder(
                        fields_subquery,
                        type_of_fields_subquery,  # type: ignore
                    )
                    fragment += f" {subquery}{{{new_fragment}}}"
            fields = [field for field in fields if "." not in field]
        for field in fields:
            try:
                type_of_fields[field]
            except KeyError as exception:
                raise NonExistingFieldError(
                    f"Cannot query field {field} on object {typed_dict_class.__name__}. Admissible"
                    " fields are: \n- " + "\n- ".join(type_of_fields.keys())
                ) from exception
            if isinstance(field, str):
                fragment += f" {field}"
            else:
                raise Exception("Please provide the fields to query as strings")
        return fragment
