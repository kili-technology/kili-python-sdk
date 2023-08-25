"""GraphQL module."""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Generator, List, NamedTuple, Optional

from typeguard import typechecked

from kili.core.constants import QUERY_BATCH_SIZE
from kili.core.graphql.graphql_client import GraphQLClient
from kili.utils.tqdm import tqdm


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK."""

    disable_tqdm: Optional[bool]
    first: Optional[int] = None
    skip: int = 0


class AbstractQueryWhere(ABC):
    """Abtsract class for defining the where payload to send in a graphQL query."""

    @abstractmethod
    def build_gql_value(self) -> Dict:
        """Build the GraphQL where payload sent in the resolver from the
        arguments given to the where class."""
        raise NotImplementedError


class PaginatedGraphQLQuery:
    """Query class for querying Kili objects.

    It factorizes code for executing paginated queries.
    """

    def __init__(self, graphql_client: GraphQLClient):
        self._graphql_client = graphql_client

    def _count(self, count_query: str, where: AbstractQueryWhere) -> int:
        """Count the number of objects matching the given where payload."""
        payload = {"where": where.build_gql_value()}
        count_result = self._graphql_client.execute(count_query, payload)
        return count_result["data"]

    def execute_query_from_paginated_call(
        self,
        query: str,
        where: AbstractQueryWhere,
        options: QueryOptions,
        nb_elements_to_query: Optional[int],
        post_call_function: Optional[Callable] = None,
    ) -> Generator[Dict, None, None]:
        """Builds a row generator from paginated calls.

        Args:
            query: The object query to execute and to send to graphQL, in string format
            where: The where payload to send in the graphQL query,
                both to the query and the count_query if specified
            options: The query options with skip and first and disable_tqdm
            nb_elements_to_query: The expected number of elements to query
            post_call_function: A function to be applied to the result of the query
        """
        disable_tqdm = nb_elements_to_query is None or options.disable_tqdm

        if nb_elements_to_query == 0:
            yield from ()
        else:
            with tqdm(total=nb_elements_to_query, disable=disable_tqdm) as pbar:
                count_elements_retrieved = 0
                while True:
                    if (
                        nb_elements_to_query is not None
                        and count_elements_retrieved >= nb_elements_to_query
                    ):
                        break

                    skip = count_elements_retrieved + options.skip
                    first = (
                        min(QUERY_BATCH_SIZE, nb_elements_to_query - count_elements_retrieved)
                        if nb_elements_to_query is not None
                        else QUERY_BATCH_SIZE
                    )
                    payload = {"where": where.build_gql_value(), "skip": skip, "first": first}
                    elements = self._graphql_client.execute(query, payload)["data"]

                    if elements is None or len(elements) == 0:
                        break

                    if post_call_function is not None:
                        elements = post_call_function(elements)

                    if isinstance(elements, Dict):
                        yield elements
                        break

                    yield from elements

                    count_elements_retrieved += len(elements)
                    pbar.update(len(elements))

                    if len(elements) < first:
                        break


def get_number_of_elements_to_query(
    graphql_client: GraphQLClient,
    where: AbstractQueryWhere,
    options: QueryOptions,
    count_query: Optional[str] = None,
):
    """Return the total number of element to query for one query that will be paginated.

    It uses both the argument first given by the user
    and the total number of available objects obtained with a graphQL count query
    """
    first = options.first
    skip = options.skip
    if count_query is not None:
        payload = {"where": where.build_gql_value()}
        count_result = graphql_client.execute(count_query, payload)
        nb_elements = count_result["data"]
        nb_elements_queried = max(nb_elements - skip, 0)
        if first is None:
            return nb_elements_queried
        return min(nb_elements_queried, first)
    if options.first is not None:
        return options.first
    return None


@typechecked
def fragment_builder(fields: List[str]):
    """Builds a GraphQL fragment for a list of fields to query.

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
            fields_subquery = [subfield[1] for subfield in subfields if subfield[0] == root_field]
            # build the subquery fragment (e.g. "user{id}" in "roles{user{id}}")
            new_fragment = fragment_builder(fields_subquery)
            # add the subquery to the fragment
            fragment += f" {root_field}{{{new_fragment}}}"

        # remove the fields that have been queried in subqueries (e.g. "roles.user.id")
        fields = [field for field in fields if "." not in field]

    for field in fields:
        fragment += f" {field}"

    return fragment
