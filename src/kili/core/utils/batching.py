"""Size-aware batching of mutation payloads and paging of query responses.

Mutations. A batched mutation closes a batch at its item cap (100) or at a byte budget of
uncompressed payload, whichever comes first. The budget follows what past mutations showed the
link and the backend can carry:

    budget = smoothed throughput (bytes / second) x TARGET_REQUEST_SECONDS,
             between MIN_BUDGET_BYTES and MAX_BUDGET_BYTES

For instance, where the last mutations moved 100 kB/s, batches weigh 1.5 MB and take about 15 s
each; at 1 MB/s and above they reach the 10 MB cap. Most batches never meet the budget: 100
assets of 5 kB weigh 500 kB, so they still go 100 at a time.

Query pages. A paginated query asks for as many items as fit a byte budget of responses, using
the size of the items measured on earlier pages of the same query:

    items per page = page budget / bytes per item, between MIN_PAGE_ITEMS and the caller's cap
    page budget    = smoothed download throughput x TARGET_REQUEST_SECONDS, at most MAX_PAGE_BYTES

The page budget starts at MAX_PAGE_BYTES and only a measured page lowers it, so on a fast link
pages keep their 100 items. For instance, where pages downloaded at 200 kB/s, items of 50 kB
come 60 to a page: 3 MB, about 15 s.
"""

import json
import threading
from collections import OrderedDict
from collections.abc import Callable, Generator, Iterable
from typing import Any, Optional, TypeVar

T = TypeVar("T")

# A batch aims at a request that completes in about this long, upload and server work included:
# a quarter of the default 60 s timeout, so a link that slows down 2-3x still makes it.
TARGET_REQUEST_SECONDS = 15.0
# Before anything is measured. Even at the slowest upload the transport plans for (100 kB/s),
# 2 MB take 20 s at most, less once compressed.
INITIAL_BUDGET_BYTES = 2_000_000
# About 2.5 s at 100 kB/s: smaller batches would spend more time on the request round trip and
# the backend's fixed cost per mutation than on their content.
MIN_BUDGET_BYTES = 256_000
# The backend holds and parses the whole uncompressed body at once: 100 items of 100 kB at most,
# however fast the link.
MAX_BUDGET_BYTES = 10_000_000
# A request smaller than this, about one round trip on a 10 Mbit/s link, is timed by latency
# rather than by throughput: it is not used to adapt the budget.
MIN_SAMPLE_BYTES = 100_000
# The budget grows slowly (it doubles in about three requests) and shrinks fast.
MAX_GROWTH_FACTOR = 1.25
# One request cannot cut a batch budget by more than this, so that a single slow request does
# not collapse it.
MAX_SHRINK_FACTOR = 0.5
# Weight of the latest request in the smoothed throughput: the budget follows the last two or
# three requests, not a single one.
THROUGHPUT_SMOOTHING = 0.5
# The page budget starts here and never exceeds it: far above what 100 items usually weigh, so
# pages are capped by their item count alone until a measured page lowers it. The first page
# measured sets the budget in one step, with no MAX_SHRINK_FACTOR.
MAX_PAGE_BYTES = 50_000_000
# On a fast but distant link (50 Mbit/s, 150 ms round trip), a smaller page downloads in about
# one round trip: its time measures latency rather than the link, so it is not used.
MIN_PAGE_SAMPLE_BYTES = 1_000_000
# A paginated query skips the items of earlier pages, which the backend scans again for every
# page: smaller pages would multiply that work more than they lighten each response. Pages of 10
# keep it within 10 times that of pages of 100.
MIN_PAGE_ITEMS = 10
# Item sizes kept per query, to size the first page of the next call of the same query. A script
# runs a handful of distinct queries: this bounds memory without forgetting any of them.
MAX_REMEMBERED_QUERIES = 128


class AdaptiveBatchSizer:
    """Byte budget for the next mutation batch, adapted to the throughput of past requests.

    Throughput is measured on the uncompressed payload over the whole request, so it folds in
    the client's uplink, the compression ratio and the time the backend spends on the batch:
    a slow link and a heavy mutation both shrink the next batch. The budget grows by at most
    MAX_GROWTH_FACTOR per request and halves on a failure.
    """

    def __init__(
        self,
        initial_bytes: int = INITIAL_BUDGET_BYTES,
        max_bytes: int = MAX_BUDGET_BYTES,
        min_sample_bytes: int = MIN_SAMPLE_BYTES,
        max_shrink_factor: float = MAX_SHRINK_FACTOR,
    ) -> None:
        self._lock = threading.Lock()
        self._initial_bytes = initial_bytes
        self._max_bytes = max_bytes
        self._min_sample_bytes = min_sample_bytes
        self._max_shrink_factor = max_shrink_factor
        self._budget_bytes = initial_bytes
        self._throughput: Optional[float] = None

    @property
    def budget_bytes(self) -> int:
        """Uncompressed size a batch, or a page, should stay under."""
        return self._budget_bytes

    def record_success(self, payload_bytes: int, elapsed_seconds: float) -> None:
        """Adapt the budget to a request that completed."""
        if payload_bytes < self._min_sample_bytes or elapsed_seconds <= 0:
            return
        with self._lock:
            throughput = payload_bytes / elapsed_seconds
            self._throughput = (
                throughput
                if self._throughput is None
                else THROUGHPUT_SMOOTHING * throughput
                + (1 - THROUGHPUT_SMOOTHING) * self._throughput
            )
            wanted = self._throughput * TARGET_REQUEST_SECONDS
            self._budget_bytes = self._clamp(
                min(
                    max(wanted, self._budget_bytes * self._max_shrink_factor),
                    self._budget_bytes * MAX_GROWTH_FACTOR,
                )
            )

    def record_failure(self, payload_bytes: Optional[int] = None) -> None:
        """Halve the budget after a request timed out or overloaded the server.

        When payload_bytes is given, a small request is ignored: its failure says nothing about
        the size of batches.
        """
        if payload_bytes is not None and payload_bytes < self._min_sample_bytes:
            return
        with self._lock:
            self._budget_bytes = self._clamp(self._budget_bytes / 2)

    def reset(self) -> None:
        """Forget what was measured."""
        with self._lock:
            self._budget_bytes = self._initial_bytes
            self._throughput = None

    def _clamp(self, budget: float) -> int:
        return int(min(self._max_bytes, max(MIN_BUDGET_BYTES, budget)))


class PageSizer:
    """Number of items per page of a paginated query, from the byte budget of responses.

    The budget adapts to the throughput of past responses, like mutation batches. Items are
    converted to bytes with the size measured on previous pages of the same query.
    """

    def __init__(self, sizer: AdaptiveBatchSizer) -> None:
        self.sizer = sizer
        self._lock = threading.Lock()
        self._bytes_per_item: OrderedDict[str, float] = OrderedDict()

    def page_size(self, query: str, max_items: int) -> int:
        """Items to ask for in the next page of this query, at most max_items."""
        bytes_per_item = self._bytes_per_item.get(query)
        if not bytes_per_item:
            return max_items  # nothing known about this query yet: the first page measures it
        fitting = int(self.sizer.budget_bytes / bytes_per_item)
        return min(max_items, max(MIN_PAGE_ITEMS, fitting))

    def record_page(self, query: str, response_bytes: int, nb_items: int) -> None:
        """Remember the size of the items of a page this query returned."""
        if nb_items <= 0 or response_bytes <= 0:
            return
        with self._lock:
            self._bytes_per_item[query] = response_bytes / nb_items
            self._bytes_per_item.move_to_end(query)
            while len(self._bytes_per_item) > MAX_REMEMBERED_QUERIES:
                self._bytes_per_item.popitem(last=False)

    def reset(self) -> None:
        """Forget what was measured."""
        self.sizer.reset()
        with self._lock:
            self._bytes_per_item.clear()


# Process-wide, like the rate limiter: every Kili client in a process shares the same link.
mutation_batch_sizer = AdaptiveBatchSizer()
# The first page measured sets the page budget: nothing limits how far it moves it down.
query_page_sizer = PageSizer(
    AdaptiveBatchSizer(
        MAX_PAGE_BYTES, MAX_PAGE_BYTES, min_sample_bytes=MIN_PAGE_SAMPLE_BYTES, max_shrink_factor=0
    )
)


def json_size(value: Any) -> int:
    """Size in bytes of the value once serialized in a request body.

    It is an estimate for batching and never raises: a value JSON cannot encode as is (a dict
    with non-string keys, say) is measured on its string form.
    """
    try:
        # ensure_ascii (the default) makes the string length equal to the encoded byte length
        return len(json.dumps(value, default=str))
    except (TypeError, ValueError):
        return len(str(value))


def size_aware_batcher(
    items: Iterable[T],
    max_items: int,
    item_size: Callable[[T], int] = json_size,
    sizer: AdaptiveBatchSizer = mutation_batch_sizer,
) -> Generator[list[T], None, None]:
    """Split items into batches capped by count and by the sizer's current byte budget.

    The budget is read when each batch closes, so a batch reflects the requests that completed
    before it closed: a caller that looks one batch ahead sizes it before the previous request.
    An item larger than the whole budget is sent alone.
    """
    batch: list[T] = []
    batch_bytes = 0
    for item in items:
        size = item_size(item)
        if batch and (len(batch) >= max_items or batch_bytes + size > sizer.budget_bytes):
            yield batch
            batch, batch_bytes = [], 0
        batch.append(item)
        batch_bytes += size
    if batch:
        yield batch


def with_is_last(iterable: Iterable[T]) -> Generator[tuple[T, bool], None, None]:
    """Yield each element with whether it is the last one."""
    iterator = iter(iterable)
    try:
        previous = next(iterator)
    except StopIteration:
        return
    for current in iterator:
        yield previous, False
        previous = current
    yield previous, True
