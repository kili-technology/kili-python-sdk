import timeit
from unittest import mock


def test_import_and_init_time_not_too_long():
    timer = timeit.Timer("from kili.client import Kili; _ = Kili()")
    time_spent = timer.timeit(number=1)

    assert time_spent < 5


@mock.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"})
def test_client_init_not_too_long_with_checks_disabled():
    timer = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent = timer.timeit(number=1)

    assert time_spent < 0.1
