import pytest

from kili.client import Kili


@pytest.fixture()
def kili() -> Kili:
    return Kili()
