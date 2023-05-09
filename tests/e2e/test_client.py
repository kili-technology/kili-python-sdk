import pyinstrument
import timeit
from unittest import mock


def test_import_and_init_time_not_too_long():
    with pyinstrument.Profiler() as profiler:
        import kili.client
        _ = kili.client.Kili()
       
    time_spent = profiler.last_session.duration
    assert time_spent < 5, profiler.output_text(unicode=True, color=True)


@mock.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"})
def test_client_init_not_too_long_with_checks_disabled():
    timer = timeit.Timer("_ = Kili()", setup="from kili.client import Kili")
    time_spent = timer.timeit(number=1)

    assert time_spent < 0.1
