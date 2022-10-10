"""
Utils
"""
import functools
import time
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, TypeVar

from kili.constants import MUTATION_BATCH_SIZE, THROTTLING_DELAY
from kili.exceptions import GraphQLError
from kili.utils.tqdm import tqdm

# pylint: disable=too-many-arguments,too-many-locals

T = TypeVar("T")


def row_generator_from_paginated_calls(
    skip: int,
    first: Optional[int],
    count_method: Callable[..., int],
    count_kwargs: dict,
    paged_call_method: Callable[..., Iterable[T]],
    paged_call_payload: dict,
    fields: List[str],
    disable_tqdm: bool,
    post_call_process: Optional[Callable[[List[T]], List[T]]] = None,
):
    """
    Builds a row generator from paginated calls.

    Args:
        skip: Number of assets to skip (they are ordered by their date of creation, first to last).
        first: Maximum number of assets to return.
        count_method: Callable returning the number of available assets given `count_args`.
        count_kwargs: Keyword arguments passed to the `count_method`.
        paged_call_method: Callable returning the list of samples.
        paged_call_payload: Payload for the GraphQL query.
        fields: The list of strings to retrieved.
        disable_tqdm: If `True`, disables tqdm.
    """
    count_rows_retrieved = 0
    if not disable_tqdm:
        count_rows_available = count_method(**count_kwargs)
        count_rows_queried_total = (
            min(count_rows_available, first) if first is not None else count_rows_available
        )
    else:
        # dummy value that won't have any impact since tqdm is disabled
        count_rows_queried_total = 1 if first != 0 else 0
    count_rows_query_default = min(100, first or 100)

    if count_rows_queried_total == 0:
        yield from ()
    else:
        with tqdm(total=count_rows_queried_total, disable=disable_tqdm) as pbar:
            while True:
                rows = api_throttle(paged_call_method)(
                    count_rows_retrieved + skip,
                    count_rows_query_default,
                    paged_call_payload,
                    fields,
                )

                if rows is None or len(rows) == 0:
                    break

                if post_call_process is not None:
                    rows = post_call_process(rows)

                for row in rows:
                    yield row

                count_rows_retrieved += len(rows)
                pbar.update(len(rows))
                if first is not None and count_rows_retrieved >= first:
                    break


def batch_iterator_builder(iterable: List, batch_size=MUTATION_BATCH_SIZE):
    """Generate an paginated iterator from a list
    Args:
        iterable: a list to paginate.
        batch_size: the size of the batches to produce
    """
    iterable_length = len(iterable)
    for ndx in range(0, iterable_length, batch_size):
        yield iterable[ndx : min(ndx + batch_size, iterable_length)]


def batch_object_builder(
    properties_to_batch: Dict[str, Optional[List[Any]]],
    batch_size: int = MUTATION_BATCH_SIZE,
) -> Iterator[Dict[str, Optional[List[Any]]]]:
    """Generate a paginated iterator for several variables
    Args:
        properties_to_batch: a dictionnary of properties to be batched.
        batch_size: the size of the batches to produce
    """
    if len(list(filter(None, properties_to_batch.values()))) == 0:
        yield properties_to_batch
        return
    number_of_objects = len([v for v in properties_to_batch.values() if v is not None][0])
    number_of_batches = len(range(0, number_of_objects, batch_size))
    batched_properties = {
        k: (
            batch_iterator_builder(v, batch_size)
            if v is not None
            else (item for item in [v] * number_of_batches)
        )
        for k, v in properties_to_batch.items()
    }
    batch_object_iterator = (
        dict(zip(batched_properties, t)) for t in zip(*batched_properties.values())
    )
    for batch in batch_object_iterator:
        yield batch  # type: ignore


def api_throttle(func):
    """
    Define a decorator that throttle a function call to meet the API limitation
    """

    @functools.wraps(func)
    def throttled_wrapper(*args, **kwargs):
        call_start = time.time()
        result = func(*args, **kwargs)
        call_duration = time.time() - call_start
        if call_duration < THROTTLING_DELAY:
            time.sleep(THROTTLING_DELAY - call_duration)
        return result

    return throttled_wrapper


def _mutate_from_paginated_call(
    self,
    properties_to_batch: Dict[str, Optional[List[Any]]],
    generate_variables: Callable,
    request: str,
    batch_size: int = MUTATION_BATCH_SIZE,
):
    """Run a mutation by making paginated calls
    Args:
        properties_to_batch: a dictionnary of properties to be batched.
            constants across batch are defined in the generate_variables function
        generate_variables: function that takes batched properties and return
            a graphQL payload for request for this batch
        request: the GraphQL request to call,
        batch_size: the size of the batches to produce
    Example:
        '''
        properties_to_batch={prop1: [0,1], prop2: ['a', 'b']}
        def generate_variables(batched_properties):
            return {
                graphQL_prop1: batched_properties['prop1']
                graphQL_prop2: batched_properties['prop2']
            }
        _mutate_from_paginated_call(
                properties_to_batch=properties_to_batch,
                generate_variables=generate_variables
                request= APPEND_MANY_TO_DATASET
                )
        '''
    """
    results = []
    for batch_number, batch in enumerate(batch_object_builder(properties_to_batch, batch_size)):
        payload = generate_variables(batch)
        result = api_throttle(self.auth.client.execute)(request, payload)
        results.append(result)
        if "errors" in result:
            raise GraphQLError(result["errors"], batch_number)
    return results
