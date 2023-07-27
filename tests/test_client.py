"""Tests for the client to return correct ee."""
import shutil
from pathlib import Path

import pytest

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


def test_no_api_key(mocker, monkeypatch):
    """Test fail because no api key is found."""
    mocker.patch("kili.client.requests")
    monkeypatch.delenv("KILI_API_KEY", raising=False)
    with pytest.raises(AuthenticationFailed):
        _ = Kili()


def test_wrong_api_key(mocker, monkeypatch):
    """Test obfuscation of api key."""
    mocker.patch("kili.client.requests")
    monkeypatch.delenv("KILI_API_KEY", raising=False)
    Kili.http_client = mocker.MagicMock()
    with pytest.raises(
        AuthenticationFailed, match=r"failed with API key: \*{9}_key"  # 9 stars for "wrong_api"
    ):
        _ = Kili(api_key="wrong_api_key")


def test_wrong_api_key_shot(mocker, monkeypatch):
    """Test no need to obfuscate api key."""
    monkeypatch.delenv("KILI_API_KEY", raising=False)
    Kili.http_client = mocker.MagicMock()
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


def test_write_to_disk_without_permissions_not_crash(mocker, monkeypatch, prepare_cache_dir):
    """Test that we can still use kili even if we don't have write permissions."""
    mocker.patch("io.open", side_effect=PermissionError("No write permissions"))
    mocker.patch("os.mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch.object(Path, "mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch.object(Kili, "_check_api_key_valid")
    mocker.patch.object(Kili, "_check_expiry_of_key_is_close")
    monkeypatch.setenv("KILI_API_KEY", "fake_key")
    _ = prepare_cache_dir

    _ = Kili(graphql_client_params={"enable_schema_caching": False})

    with pytest.raises(PermissionError):
        _ = Kili()
