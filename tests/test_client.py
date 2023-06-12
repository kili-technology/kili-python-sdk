"""Tests for the client to return correct ee."""
import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from kili.client import Kili
from kili.core.authentication import KiliAuth
from kili.exceptions import AuthenticationFailed


@patch("kili.core.authentication.requests")
def test_no_api_key(mocked_requests):
    """Test fail because no api key is found."""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(AuthenticationFailed):
            _ = Kili()


@patch("kili.core.authentication.requests")
def test_wrong_api_key(mocked_requests):
    """Test obfuscation of api key."""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(
            AuthenticationFailed, match=r"failed with API key: \*{9}_key"  # 9 stars for "wrong_api"
        ):
            _ = Kili(api_key="wrong_api_key")


@patch("kili.core.authentication.requests")
def test_wrong_api_key_shot(mocked_requests):
    """Test no need to obfuscate api key."""
    with patch.dict(os.environ):
        os.environ.pop("KILI_API_KEY", None)
        with pytest.raises(AuthenticationFailed, match="failed with API key: no"):
            _ = Kili(api_key="no")


@pytest.fixture
def prepare_cache_dir():
    """Prepare cache dir."""
    kili_cache_dir = Path.home() / ".cache" / "kili"
    if kili_cache_dir.exists():
        shutil.rmtree(kili_cache_dir)

    yield

    if kili_cache_dir.exists():
        shutil.rmtree(kili_cache_dir)


@patch("io.open", side_effect=PermissionError("No write permissions"))
@patch("os.mkdir", side_effect=PermissionError("No write permissions"))
@patch.object(Path, "mkdir", side_effect=PermissionError("No write permissions"))
@patch.object(KiliAuth, "check_api_key_valid")
@patch.object(KiliAuth, "check_expiry_of_key_is_close")
@patch.dict(os.environ, {"KILI_API_KEY": "fake_key"})
def test_write_to_disk_without_permissions_not_crash(*_):
    """Test that we can still use kili even if we don't have write permissions."""
    _ = Kili(graphql_client_params={"enable_schema_caching": False})

    with pytest.raises(PermissionError):
        _ = Kili()
