import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_mock

from kili.client import Kili
from kili.exceptions import AuthenticationFailed


@patch.dict(os.environ, {"KILI_API_KEY": "", "KILI_SDK_SKIP_CHECKS": "True"})
def test_no_api_key(mocker: pytest_mock.MockerFixture):
    """Test fail because no api key is found."""
    mocker.patch("kili.client.requests")
    mocker.patch("kili.client.getpass.getpass", return_value="")
    with pytest.raises(AuthenticationFailed):
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "wrong_api_key"})
def test_wrong_api_key_is_obfuscated(mocker: pytest_mock.MockerFixture):
    """Test obfuscation of api key."""
    mocker.patch.object(Kili, "_check_api_key_valid", return_value=False)
    with pytest.raises(
        AuthenticationFailed, match=r"failed with API key: \*{9}_key"  # 9 stars for "wrong_api"
    ):
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "no"})
def test_wrong_api_key_no_need_to_obfuscate(mocker: pytest_mock.MockerFixture):
    """Test no need to obfuscate api key."""
    mocker.patch.object(Kili, "_check_api_key_valid", return_value=False)
    with pytest.raises(AuthenticationFailed, match="failed with API key: no"):
        _ = Kili()


@pytest.fixture
def prepare_cache_dir():
    """Prepare cache dir."""
    kili_cache_dir = Path.home() / ".cache" / "kili"
    if kili_cache_dir.exists():
        shutil.rmtree(kili_cache_dir)

    yield

    if kili_cache_dir.exists():
        shutil.rmtree(kili_cache_dir)


@patch.dict(os.environ, {"KILI_API_KEY": "fake_key"})
def test_write_to_disk_without_permissions_not_crash(
    prepare_cache_dir, mocker: pytest_mock.MockerFixture
):
    """Test that we can still use kili even if we don't have write permissions."""
    mocker.patch("io.open", side_effect=PermissionError("No write permissions"))
    mocker.patch("os.mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch.object(Path, "mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch.object(Kili, "_check_api_key_valid")
    mocker.patch.object(Kili, "_check_expiry_of_key_is_close")

    # caching disabled, should work
    _ = Kili(graphql_client_params={"enable_schema_caching": False})

    # will crash trying to cache the schema
    with pytest.raises(PermissionError):
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "", "KILI_SDK_SKIP_CHECKS": "True"})
def test_given_env_without_api_key_when_initializing_kili_client_then_it_asks_for_api_key_getpass(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("kili.client.sys.stdin.isatty", return_value=True)
    mocker_getpass = mocker.patch(
        "kili.client.getpass.getpass", return_value="fake_key_entered_by_user"
    )

    # When
    _ = Kili()

    # Then
    mocker_getpass.assert_called_once()


@patch.dict(os.environ, {"KILI_API_KEY": "", "KILI_SDK_SKIP_CHECKS": "True"})
def test_given_non_tti_env_without_api_key_when_initializing_kili_client_then_it_crash(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("kili.client.sys.stdin.isatty", return_value=False)
    with pytest.raises(AuthenticationFailed):
        _ = Kili()
