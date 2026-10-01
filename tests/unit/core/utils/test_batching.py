from kili.core.utils.batching import (
    INITIAL_BUDGET_BYTES,
    MAX_BUDGET_BYTES,
    MIN_BUDGET_BYTES,
    TARGET_REQUEST_SECONDS,
    AdaptiveBatchSizer,
    json_size,
    size_aware_batcher,
    with_is_last,
)


def test_budget_follows_a_slow_link_down():
    sizer = AdaptiveBatchSizer()

    sizer.record_success(20_000_000, 300)

    assert sizer.budget_bytes == int(20_000_000 / 300 * TARGET_REQUEST_SECONDS)


def test_one_request_cuts_the_budget_by_half_at_most():
    sizer = AdaptiveBatchSizer()

    sizer.record_success(200_000, 60)  # about 3 kB/s: a latency-bound or stalled request

    assert sizer.budget_bytes == INITIAL_BUDGET_BYTES // 2


def test_budget_grows_by_at_most_a_quarter_per_request():
    sizer = AdaptiveBatchSizer()

    sizer.record_success(2_000_000, 0.1)
    assert sizer.budget_bytes == int(INITIAL_BUDGET_BYTES * 1.25)

    for _ in range(50):
        sizer.record_success(2_000_000, 0.1)
    assert sizer.budget_bytes == MAX_BUDGET_BYTES


def test_small_requests_do_not_move_the_budget():
    sizer = AdaptiveBatchSizer()

    sizer.record_success(10_000, 30)

    assert sizer.budget_bytes == INITIAL_BUDGET_BYTES


def test_budget_halves_on_failure_down_to_the_floor():
    sizer = AdaptiveBatchSizer()

    sizer.record_failure(1_000_000)
    assert sizer.budget_bytes == INITIAL_BUDGET_BYTES // 2

    for _ in range(10):
        sizer.record_failure(1_000_000)
    assert sizer.budget_bytes == MIN_BUDGET_BYTES


def test_a_small_request_that_fails_does_not_shrink_batches():
    sizer = AdaptiveBatchSizer()

    sizer.record_failure(10_000)

    assert sizer.budget_bytes == INITIAL_BUDGET_BYTES


def test_batches_are_capped_by_count():
    batches = list(size_aware_batcher(range(7), max_items=3, item_size=lambda _: 1))

    assert batches == [[0, 1, 2], [3, 4, 5], [6]]


def test_batches_are_capped_by_size_and_an_oversized_item_goes_alone():
    sizer = AdaptiveBatchSizer()
    sizes = {"a": 900_000, "b": 900_000, "c": 900_000, "big": 5_000_000, "d": 10}

    batches = list(size_aware_batcher(sizes, 100, item_size=sizes.__getitem__, sizer=sizer))

    assert batches == [["a", "b"], ["c"], ["big"], ["d"]]


def test_budget_changes_apply_to_the_next_batch():
    sizer = AdaptiveBatchSizer()
    batches = size_aware_batcher(range(10), 100, item_size=lambda _: 600_000, sizer=sizer)

    assert next(batches) == [0, 1, 2]  # 1.8 MB under the initial 2 MB
    sizer.record_failure(1_000_000)  # the budget drops to 1 MB
    assert next(batches) == [3]
    assert next(batches) == [4]


def test_json_size_counts_serialized_bytes():
    assert json_size({"a": "é"}) == len('{"a": "\\u00e9"}')


def test_json_size_never_raises():
    assert json_size({("tuple", "key"): 1}) == len(str({("tuple", "key"): 1}))


def test_with_is_last():
    assert list(with_is_last([])) == []
    assert list(with_is_last(["a"])) == [("a", True)]
    assert list(with_is_last(["a", "b"])) == [("a", False), ("b", True)]
