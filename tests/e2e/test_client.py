import timeit
from unittest import mock

from kili.client import Kili
from pyinstrument.profiler import Profiler


def test_import_and_init_time_not_too_long():
    _ = Kili()  # cache the schema
    
    with Profiler() as profiler:
        _ = Kili()

    time_spent = profiler.last_session.duration  # type: ignore
    assert time_spent < 5, profiler.output_text(unicode=False)


@mock.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"})
def test_client_init_not_too_long_with_checks_disabled():
    timer = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent = timer.timeit(number=1)

    assert time_spent < 0.1
