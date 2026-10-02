from kili.core.utils.batching import (
    INITIAL_BUDGET_BYTES,
    MAX_BUDGET_BYTES,
    MAX_PAGE_BYTES,
    MAX_REMEMBERED_QUERIES,
    MIN_BUDGET_BYTES,
    MIN_PAGE_ITEMS,
    MIN_PAGE_SAMPLE_BYTES,
    TARGET_REQUEST_SECONDS,
    AdaptiveBatchSizer,
    PageSizer,
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


def _page_budget() -> AdaptiveBatchSizer:
    """Configured like the page budget of queries."""
    return AdaptiveBatchSizer(
        MAX_PAGE_BYTES, MAX_PAGE_BYTES, min_sample_bytes=MIN_PAGE_SAMPLE_BYTES, max_shrink_factor=0
    )


def test_page_size_follows_the_budget_and_the_measured_items():
    pages = PageSizer(_page_budget())

    assert pages.page_size("q", 100) == 100  # unknown items: the item cap
    pages.record_page("q", 500_000, 10)  # 50 kB per item
    assert pages.page_size("q", 100) == 100  # the budget starts unrestricted

    pages.sizer.record_success(20_000_000, 300)  # a slow link: about 1 MB per page
    assert pages.page_size("q", 100) == 20
    assert pages.page_size("other query", 100) == 100


def test_pages_keep_a_few_items_even_when_one_is_heavier_than_the_budget():
    pages = PageSizer(_page_budget())
    pages.sizer.record_success(20_000_000, 300)

    pages.record_page("q", 100_000_000, 1)

    assert pages.page_size("q", 100) == MIN_PAGE_ITEMS
    assert pages.page_size("q", 3) == 3  # the caller's cap still wins


def test_the_first_page_measured_sets_the_page_budget():
    budget = _page_budget()

    budget.record_success(20_000_000, 100)  # 200 kB/s

    assert budget.budget_bytes == int(20_000_000 / 100 * TARGET_REQUEST_SECONDS)


def test_a_small_page_does_not_move_the_page_budget():
    budget = _page_budget()

    budget.record_success(300_000, 0.3)  # a round trip more than a download

    assert budget.budget_bytes == MAX_PAGE_BYTES


def test_page_sizer_remembers_a_bounded_number_of_queries():
    pages = PageSizer(AdaptiveBatchSizer())  # a 2 MB budget

    for i in range(MAX_REMEMBERED_QUERIES + 10):
        pages.record_page(f"query {i}", 100_000, 1)

    assert pages.page_size("query 0", 100) == 100  # forgotten
    assert pages.page_size(f"query {MAX_REMEMBERED_QUERIES + 9}", 100) == 20
