import os

import pytest

from kili.client import Kili


@pytest.fixture(scope="session")
def kili() -> Kili:
    """Kili client with user rights."""
    return Kili()


@pytest.fixture(scope="session")
def kili_admin() -> Kili:
    """Kili client with admin rights."""
    return Kili(api_key=os.environ["KILI_API_KEY_ADMIN"])
