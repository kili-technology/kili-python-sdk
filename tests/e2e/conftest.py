import pytest

from kili.client import Kili


@pytest.fixture(scope="session")
def kili() -> Kili:
    return Kili()
