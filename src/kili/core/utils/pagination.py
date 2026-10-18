"""Pagination utils."""

from collections.abc import Callable, Generator, Iterable
from itertools import islice
from time import sleep
from typing import Any, Optional, TypeVar

from kili.core.constants import MUTATION_BATCH_SIZE
from kili.core.utils.batching import json_size, size_aware_batcher
from kili.domain.types import ListOrTuple
from kili.exceptions import GraphQLError, MutationOutcomeUnknownError


def batch_object_builder(
    properties_to_batch: dict[str, ListOrTuple[Any]],
    batch_size: int = MUTATION_BATCH_SIZE,
) -> Generator[dict[str, Any], None, None]:
    """Generate batches of several variables, capped by count and by payload size.

    Args:
        properties_to_batch: a dictionary of properties to be batched. A property set to None
            stays None in every batch.
        batch_size: the maximum number of objects in a batch
    """
    batched = {k: v for k, v in properties_to_batch.items() if v is not None}
    if not any(batched.values()):
        yield properties_to_batch
        return
    # pylint: disable=stop-iteration-return
    number_of_objects = len(next(v for v in batched.values() if v))

    def object_size(index: int) -> int:
        return json_size({k: v[index] for k, v in batched.items() if index < len(v)})

    for indexes in size_aware_batcher(range(number_of_objects), batch_size, object_size):
        yield {
            k: (None if v is None else [v[i] for i in indexes if i < len(v)])
            for k, v in properties_to_batch.items()
        }


def _batch_length(batch: dict[str, Any]) -> int:
    return max((len(v) for v in batch.values() if isinstance(v, list)), default=0)


# pylint: disable=missing-type-doc
def mutate_from_paginated_call(
    kili,
    properties_to_batch: dict[str, ListOrTuple[Any]],
    generate_variables: Callable,
    request: str,
    batch_size: int = MUTATION_BATCH_SIZE,
    last_batch_callback: Optional[Callable] = None,
) -> list:
    """Run a mutation by making paginated calls.

    Args:
        kili: kili
        properties_to_batch: a dictionary of properties to be batched.
            constants across batch are defined in the generate_variables function
        generate_variables: function that takes batched properties and return
            a graphQL payload for request for this batch
        request: the GraphQL request to call,
        batch_size: the size of the batches to produce
        last_batch_callback: a function that takes the last batch and the result of
            this method as arguments

    Example:
        ```python
        properties_to_batch={prop1: [0,1], prop2: ['a', 'b']}
        def generate_variables(batched_properties):
            return {
                graphQL_prop1: batched_properties['prop1']
                graphQL_prop2: batched_properties['prop2']
            }
        mutate_from_paginated_call(
                properties_to_batch=properties_to_batch,
                generate_variables=generate_variables
                request= GQL_APPEND_MANY_ASSETS
        )
        ```
    """
    results = []
    batch = None
    first_index = 0
    for batch in batch_object_builder(properties_to_batch, batch_size):
        payload = generate_variables(batch)
        try:
            result = kili.graphql_client.execute(request, payload)
        except GraphQLError as err:
            raise GraphQLError(error=err.error, index=first_index) from err
        except MutationOutcomeUnknownError as err:
            raise err.at_index(first_index) from err.cause
        results.append(result)
        first_index += _batch_length(batch)

    sleep(1)  # wait for the backend to process the mutations
    if batch and results and last_batch_callback:
        last_batch_callback(batch, results)
    return results


T = TypeVar("T")


def batcher(iterable: Iterable[T], batch_size: int) -> Generator[list[T], None, None]:
    """Break iterable into sub-iterables with batch_size elements each.

    The last yielded list will have fewer than n elements if the
    length of iterable is not divisible by batch_size:
    """
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch
