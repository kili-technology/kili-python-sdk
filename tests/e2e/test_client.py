import timeit
from unittest import mock


def test_client_init_not_too_long():
    timer = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent = timer.timeit(number=1)

    assert time_spent < 2


def test_import_and_init_time_not_too_long():
    timer = timeit.Timer("from kili.client import Kili; _ = Kili()")
    time_spent = timer.timeit(number=1)

    assert time_spent < 3


@mock.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"})
def test_client_init_not_too_long_with_checks_disabled():
    timer = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent = timer.timeit(number=1)

    assert time_spent < 0.1


def test_client_with_checks_disabled_always_faster_than_with_checks_enabled():
    timer_with_checks = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent_with_checks = timer_with_checks.timeit(number=1)

    with mock.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"}):
        timer_without_checks = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
        time_spent_without_checks = timer_without_checks.timeit(number=1)

    assert time_spent_with_checks > 10 * time_spent_without_checks  # one order of magnitude
