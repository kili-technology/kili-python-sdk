"""GraphQL module."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generator, List, NamedTuple, Optional

from typeguard import typechecked

from kili.core.constants import QUERY_BATCH_SIZE
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.types import ListOrTuple
from kili.utils.tqdm import tqdm


class QueryOptions(NamedTuple):
    """Options when calling GraphQLQuery from the SDK."""

    disable_tqdm: Optional[bool]
    first: Optional[int] = None
    skip: int = 0


class AbstractQueryWhere(ABC):
    """Abtsract class for defining the where payload to send in a graphQL query."""

    @abstractmethod
    def build_gql_where(self):
        """Build the GraphQL where variable sent in the resolver from the
        arguments given to the where class."""
        raise NotImplementedError


class PaginatedGraphQLQuery:
    """Query class for querying Kili objects.

    It factorizes code for executing paginated queries.
    """

    def __init__(self, graphql_client: GraphQLClient):
        self._graphql_client = graphql_client

    # pylint: disable=too-many-arguments
    def execute_query_from_paginated_call(
        self,
        query: str,
        where: Dict[str, Any],
        options: QueryOptions,
        tqdm_desc: str,
        nb_elements_to_query: Optional[int],
        post_call_function: Optional[Callable[[List], List]] = None,
    ) -> Generator[Dict, None, None]:
        """Build a row generator from paginated calls.

        Args:
            query: The object query to execute and to send to graphQL, in string format
            where: The where payload to send in the graphQL query
            options: The query options with skip and first and disable_tqdm
            tqdm_desc: The description to show in the progress bar
            nb_elements_to_query: The expected number of elements to query.
                If given, it will show a progress bar if tqdm is not disabled in options
            post_call_function: A function to be applied to the result of the query after each call.
                It should take the elements of the result of the query as input and should return
                the list of modified (or not) elements
        """
        disable_tqdm = nb_elements_to_query is None or options.disable_tqdm

        if nb_elements_to_query == 0:
            yield from ()
        else:
            with tqdm(total=nb_elements_to_query, disable=disable_tqdm, desc=tqdm_desc) as pbar:
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
                    payload = {"where": where, "skip": skip, "first": first}
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
    count_query: str,
    where: Dict[str, Any],
    options: QueryOptions,
) -> int:
    """Give the total number of elements to query for one query that will be paginated.

    It uses both the argument first given by the user
    and the total number of available objects obtained with a graphQL count query

    Args:
        graphql_client: The graphQL client
        where: the where payload to the count query,
        options: the query options with skip and first
        count_query: the count query

    Returns:
        The number of elements to query
    """
    first = options.first
    skip = options.skip
    payload = {"where": where}
    count_result = graphql_client.execute(count_query, payload)
    nb_elements = count_result["data"]
    nb_elements_queried = max(nb_elements - skip, 0)
    if first is None:
        return nb_elements_queried
    return min(nb_elements_queried, first)


@typechecked
def fragment_builder(fields: ListOrTuple[str]) -> str:
    """Build a GraphQL fragment for a list of fields to query.

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
