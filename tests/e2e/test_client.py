import pytest_mock
from pyinstrument.profiler import Profiler

from kili.client import Kili


def test_client_init_not_too_long_with_checks_enabled():
    _ = Kili()  # cache the graphql schema

    with Profiler() as profiler:
        _ = Kili()

    time_spent = profiler.last_session.duration  # type: ignore
    assert time_spent < 5, profiler.output_text(unicode=False)


def test_client_init_not_too_long_with_checks_disabled(mocker: pytest_mock.MockerFixture):
    mocker.patch.dict("os.environ", {"KILI_SDK_SKIP_CHECKS": "True"})

    with Profiler() as profiler:
        _ = Kili()

    time_spent = profiler.last_session.duration  # type: ignore
    assert time_spent < 0.5, profiler.output_text(unicode=False)
