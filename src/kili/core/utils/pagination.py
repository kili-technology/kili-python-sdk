"""Pagination utils."""
from itertools import islice
from time import sleep
from typing import Any, Callable, Dict, Iterator, List, Optional

from kili.core.constants import MUTATION_BATCH_SIZE
from kili.exceptions import GraphQLError

# pylint: disable=too-many-arguments


class BatchIteratorBuilder:
    """Generate an paginated iterator from a list.

    Args:
        iterable: a list to paginate.
        batch_size: the size of the batches to produce
    """

    def __init__(self, iterable: List, batch_size: int = MUTATION_BATCH_SIZE) -> None:
        self.iterable = iterable
        self.batch_size = batch_size
        self.nb_batches = (len(iterable) - 1) // batch_size + 1

    def __len__(self) -> int:
        return self.nb_batches

    def __next__(self):
        next_batch = self.iterable[: self.batch_size]
        self.iterable = self.iterable[self.batch_size :]
        if len(next_batch) > 0:
            return next_batch
        raise StopIteration

    def __iter__(self):
        return self


def batch_object_builder(
    properties_to_batch: Dict[str, Optional[List[Any]]],
    batch_size: int = MUTATION_BATCH_SIZE,
) -> Iterator[Dict[str, Optional[List[Any]]]]:
    """Generate a paginated iterator for several variables.

    Args:
        properties_to_batch: a dictionary of properties to be batched.
        batch_size: the size of the batches to produce
    """
    if len(list(filter(None, properties_to_batch.values()))) == 0:
        yield properties_to_batch
        return
    # pylint: disable=stop-iteration-return
    number_of_objects = len(next(v for v in properties_to_batch.values() if v is not None))
    number_of_batches = len(range(0, number_of_objects, batch_size))
    batched_properties = {
        k: (
            BatchIteratorBuilder(iterable=v, batch_size=batch_size)
            if v is not None
            else (item for item in [v] * number_of_batches)
        )
        for k, v in properties_to_batch.items()
    }
    batch_object_iterator = (
        dict(zip(batched_properties, t)) for t in zip(*batched_properties.values())
    )
    yield from batch_object_iterator


# pylint: disable=missing-type-doc
def mutate_from_paginated_call(
    kili,
    properties_to_batch: Dict[str, Optional[List[Any]]],
    generate_variables: Callable,
    request: str,
    batch_size: int = MUTATION_BATCH_SIZE,
    last_batch_callback: Optional[Callable] = None,
) -> List:
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
    for batch_number, batch in enumerate(batch_object_builder(properties_to_batch, batch_size)):
        payload = generate_variables(batch)
        try:
            result = kili.graphql_client.execute(request, payload)
        except GraphQLError as err:
            raise GraphQLError(error=err.error, batch_number=batch_number) from err
        results.append(result)

    sleep(1)  # wait for the backend to process the mutations
    if batch and results and last_batch_callback:
        last_batch_callback(batch, results)
    return results


def batcher(iterable: Iterator, batch_size: int):
    """Break iterable into sub-iterables with batch_size elements each.

    The last yielded list will have fewer than n elements if the
    length of iterable is not divisible by batch_size:
    """
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch
