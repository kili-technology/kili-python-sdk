"""Pytest configuration and shared fixtures for domain_v2 integration tests.

This module provides fixtures for testing domain_v2 View objects against
the real Kili API using test credentials.

Test Configuration:
    API_KEY:
    ENDPOINT: http://localhost:4001/api/label/v2/graphql
"""

import os
from typing import Generator

import pytest

from kili.client_domain import Kili

# Test configuration constants
TEST_API_KEY = ""
TEST_ENDPOINT = "http://localhost:4001/api/label/v2/graphql"


@pytest.fixture(scope="session")
def api_key() -> str:
    """Provide the API key for test authentication.

    Returns:
        Test API key for integration tests

    Example:
        >>> def test_with_api_key(api_key):
        ...     assert api_key == TEST_API_KEY
    """
    return TEST_API_KEY


@pytest.fixture(scope="session")
def api_endpoint() -> str:
    """Provide the API endpoint for test server.

    Returns:
        Test API endpoint URL

    Example:
        >>> def test_with_endpoint(api_endpoint):
        ...     assert api_endpoint == TEST_ENDPOINT
    """
    return TEST_ENDPOINT


@pytest.fixture(scope="session")
def kili_client(api_key: str, api_endpoint: str) -> Generator[Kili, None, None]:
    """Provide a configured Kili client for integration tests.

    This fixture creates a Kili client instance using the test credentials
    and yields it for use in tests. The client uses the domain API with
    namespace organization.

    Args:
        api_key: Test API key (from api_key fixture)
        api_endpoint: Test endpoint URL (from api_endpoint fixture)

    Yields:
        Configured Kili client instance

    Example:
        >>> def test_assets(kili_client):
        ...     assets = kili_client.assets.list(first=10)
        ...     assert isinstance(assets, list)
    """
    # Temporarily override environment variables if needed
    original_key = os.environ.get("KILI_API_KEY")
    original_endpoint = os.environ.get("KILI_API_ENDPOINT")

    try:
        # Create client with test credentials
        client = Kili(api_key=api_key, api_endpoint=api_endpoint)
        yield client
    finally:
        # Restore original environment variables
        if original_key is not None:
            os.environ["KILI_API_KEY"] = original_key
        elif "KILI_API_KEY" in os.environ:
            del os.environ["KILI_API_KEY"]

        if original_endpoint is not None:
            os.environ["KILI_API_ENDPOINT"] = original_endpoint
        elif "KILI_API_ENDPOINT" in os.environ:
            del os.environ["KILI_API_ENDPOINT"]


@pytest.fixture()
def skip_if_no_data(kili_client: Kili, entity_type: str):
    """Skip test if no test data exists for the entity type.

    This fixture can be parametrized to check for specific entity types
    (projects, assets, labels, users) and skip tests gracefully when no
    data is available.

    Args:
        kili_client: Configured Kili client
        entity_type: Type of entity to check ('projects', 'assets', 'labels', 'users')

    Raises:
        pytest.skip: If no data exists for the entity type

    Example:
        >>> @pytest.mark.parametrize("entity_type", ["projects"])
        >>> def test_projects(kili_client, skip_if_no_data):
        ...     # Test will be skipped if no projects exist
        ...     projects = kili_client.projects.list(first=1)
    """
    # This is a marker fixture - actual implementation in individual tests
    # Each test can choose to use this pattern to skip when no data exists


# Configure pytest to show more detailed output
def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "requires_data: mark test as requiring existing test data")
