"""
Utils
"""
from typing import List, Callable, Optional
import time
from tqdm import tqdm

from .helpers import GraphQLError
from .constants import MUTATION_BATCH_SIZE, THROTTLING_DELAY

# pylint: disable=too-many-arguments,too-many-locals


def row_generator_from_paginated_calls(
    skip: int,
    first: int,
    count_method: Callable[..., int],
    count_kwargs: dict,
    paged_call_method: Callable[..., List[dict]],
    paged_call_payload: dict,
    fields: List[str],
    disable_tqdm: bool,
):
    """Build a row generator from paginated query calls.

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
        count_rows_queried_total = min(count_rows_available,
                                       first) if first is not None else count_rows_available
    else:
        # dummy value that won't have any impact since tqdm is disabled
        count_rows_queried_total = 1 if first != 0 else 0
    count_rows_query_default = min(100, first or 100)

    if count_rows_queried_total == 0:
        yield from ()
    else:
        with tqdm(total=count_rows_queried_total, disable=disable_tqdm) as pbar:
            while True:
                query_start = time.time()
                rows = paged_call_method(
                    count_rows_retrieved + skip,
                    count_rows_query_default,
                    paged_call_payload,
                    fields,
                )
                query_time = time.time() - query_start

                if query_time < THROTTLING_DELAY:
                    time.sleep(THROTTLING_DELAY - query_time)

                if rows is None or len(rows) == 0:
                    break

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
        yield iterable[ndx:min(ndx + batch_size, iterable_length)]


def batch_iterators_builder(
        properties_to_batch: dict[Optional[List]],
        batch_size=MUTATION_BATCH_SIZE) -> dict[Optional[List]]:
    """Generate a paginated iterator for several variables

    Args:
        arrays: a list of arrays to paginate. Arrays can be None
        batch_size: the size of the batches to produce
    """
    if len(list(filter(None, properties_to_batch.values()))) == 0:
        return properties_to_batch
    number_of_objects = len([v for v in properties_to_batch.values(
    ) if v is not None][0])
    number_of_batches = len(range(0, number_of_objects, batch_size))
    batched_properties = {k: (batch_iterator_builder(v, batch_size) if v is not None
                              else (item for item in [v]*number_of_batches))
                          for k, v in properties_to_batch.items()}
    for _ in range(number_of_batches):
        yield {k: next(v) for k, v in batched_properties.items()}


def _mutate_from_paginated_call(self, properties_to_batch, generate_variables, request):
    results = []
    for batch_number, batch in enumerate(batch_iterators_builder(properties_to_batch)):
        mutation_start = time.time()
        variables = generate_variables(batch)
        result = self.auth.client.execute(request, variables)
        mutation_time = time.time() - mutation_start
        results.append(result)
        if 'errors' in result:
            raise GraphQLError('data', result['errors'], batch_number)
        if mutation_time < THROTTLING_DELAY:
            time.sleep(THROTTLING_DELAY - mutation_time)
    return results
