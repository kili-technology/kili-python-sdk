"""
Utils
"""
from typing import List, Callable

import time
from tqdm import tqdm

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
        count_rows_queried_total = min(count_rows_available,
                                       first) if first is not None else count_rows_available
    else:
        # dummy value that won't have any impact since tqdm is disabled
        count_rows_queried_total = 1 if first != 0 else 0
    count_rows_query_default = min(100, first or 100)
    throttling_delay = 60 / 250

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

                if query_time < throttling_delay:
                    time.sleep(throttling_delay - query_time)

                if rows is None or len(rows) == 0:
                    break

                for row in rows:
                    yield row

                count_rows_retrieved += len(rows)
                pbar.update(len(rows))
                if first is not None and count_rows_retrieved >= first:
                    break
