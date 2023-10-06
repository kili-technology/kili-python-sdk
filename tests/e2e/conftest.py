import os

import pytest

from kili.client import Kili


@pytest.fixture(scope="session")
def kili() -> Kili:
    return Kili()


@pytest.fixture(scope="session")
def kili_admin() -> Kili:
    return Kili(api_key=os.environ["KILI_API_KEY_ADMIN"])
