"""Pytest configuration for equivalence tests.

This module provides fixtures and configuration for running equivalence tests.
"""

import os

import pytest


def pytest_configure(config):
    """Configure pytest for equivalence tests."""
    config.addinivalue_line("markers", "equivalence: mark test as an equivalence test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring API access"
    )


@pytest.fixture(scope="session")
def recordings_dir(tmp_path_factory):
    """Provide a temporary directory for test recordings."""
    return tmp_path_factory.mktemp("recordings")


@pytest.fixture()
def use_real_api():
    """Check if tests should use real API (based on env var)."""
    return os.getenv("KILI_USE_REAL_API", "false").lower() == "true"


@pytest.fixture()
def api_key():
    """Get API key from environment."""
    return os.getenv("KILI_API_KEY")


@pytest.fixture()
def api_endpoint():
    """Get API endpoint from environment."""
    return os.getenv("KILI_API_ENDPOINT", "https://cloud.kili-technology.com/api/label/v2/graphql")


@pytest.fixture()
def test_project_id():
    """Get test project ID from environment."""
    return os.getenv("KILI_TEST_PROJECT_ID")


@pytest.fixture()
def skip_if_no_api(use_real_api, api_key):  # pylint: disable=redefined-outer-name
    """Skip test if API access is not configured."""
    if not use_real_api or not api_key:
        pytest.skip("Skipping test: API access not configured")
