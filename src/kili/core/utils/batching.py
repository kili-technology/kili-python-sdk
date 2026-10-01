"""Size-aware batching of mutation payloads.

A batched mutation closes a batch at its item cap (100) or at a byte budget of uncompressed
payload, whichever comes first. The budget follows what past mutations showed the link and the
backend can carry:

    budget = smoothed throughput (bytes / second) x TARGET_REQUEST_SECONDS,
             between MIN_BUDGET_BYTES and MAX_BUDGET_BYTES

For instance, where the last mutations moved 100 kB/s, batches weigh 1.5 MB and take about 15 s
each; at 1 MB/s and above they reach the 10 MB cap. Most batches never meet the budget: 100
assets of 5 kB weigh 500 kB, so they still go 100 at a time.
"""

import json
import threading
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


class AdaptiveBatchSizer:
    """Byte budget for the next mutation batch, adapted to the throughput of past requests.

    Throughput is measured on the uncompressed payload over the whole request, so it folds in
    the client's uplink, the compression ratio and the time the backend spends on the batch:
    a slow link and a heavy mutation both shrink the next batch. The budget grows by at most
    MAX_GROWTH_FACTOR per request and halves on a failure.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._budget_bytes = INITIAL_BUDGET_BYTES
        self._throughput: Optional[float] = None

    @property
    def budget_bytes(self) -> int:
        """Uncompressed size a batch should stay under."""
        return self._budget_bytes

    def record_success(self, payload_bytes: int, elapsed_seconds: float) -> None:
        """Adapt the budget to a request that completed."""
        if payload_bytes < MIN_SAMPLE_BYTES or elapsed_seconds <= 0:
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
                    max(wanted, self._budget_bytes * MAX_SHRINK_FACTOR),
                    self._budget_bytes * MAX_GROWTH_FACTOR,
                )
            )

    def record_failure(self, payload_bytes: int) -> None:
        """Halve the budget after a large request timed out or overloaded the server."""
        if payload_bytes < MIN_SAMPLE_BYTES:
            return  # a small request that fails says nothing about the size of batches
        with self._lock:
            self._budget_bytes = self._clamp(self._budget_bytes / 2)

    def reset(self) -> None:
        """Forget what was measured."""
        with self._lock:
            self._budget_bytes = INITIAL_BUDGET_BYTES
            self._throughput = None

    @staticmethod
    def _clamp(budget: float) -> int:
        return int(min(MAX_BUDGET_BYTES, max(MIN_BUDGET_BYTES, budget)))


# Process-wide, like the rate limiter: every Kili client in a process shares the same link.
mutation_batch_sizer = AdaptiveBatchSizer()


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
