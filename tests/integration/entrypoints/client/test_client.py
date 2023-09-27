import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_mock
from filelock import FileLock

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.core.graphql.graphql_client import (
    DEFAULT_GRAPHQL_SCHEMA_CACHE_DIR,
    GraphQLClient,
)
from kili.exceptions import AuthenticationFailed
from kili.use_cases.api_key import ApiKeyUseCases


@patch.dict(os.environ, {"KILI_API_KEY": "", "KILI_SDK_SKIP_CHECKS": "True"})
def test_no_api_key(mocker: pytest_mock.MockerFixture):
    """Test fail because no api key is found."""
    mocker.patch("kili.adapters.http_client.requests")
    mocker.patch("kili.client.getpass.getpass", return_value="")
    with pytest.raises(AuthenticationFailed):
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "wrong_api_key"})
def test_wrong_api_key_is_obfuscated(mocker: pytest_mock.MockerFixture):
    mocker.patch("kili.client.is_api_key_valid", return_value=False)
    """Test obfuscation of api key."""
    with pytest.raises(
        AuthenticationFailed, match=r"failed with API key: \*{9}_key"  # 9 stars for "wrong_api"
    ):
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "no"})
def test_wrong_api_key_no_need_to_obfuscate(mocker: pytest_mock.MockerFixture):
    """Test no need to obfuscate api key."""
    mocker.patch("kili.client.is_api_key_valid", return_value=False)
    with pytest.raises(AuthenticationFailed, match="failed with API key: no"):
        _ = Kili()


@pytest.fixture()
def prepare_cache_dir():
    """Prepare cache dir."""

    def purge_cache_dir():
        with FileLock(DEFAULT_GRAPHQL_SCHEMA_CACHE_DIR / "cache_dir.lock", timeout=15):
            files_in_cache_dir = list(DEFAULT_GRAPHQL_SCHEMA_CACHE_DIR.glob("*"))
            files_to_delete = [f for f in files_in_cache_dir if "cache_dir.lock" not in f.name]

            for f in files_to_delete:
                f.unlink()

    purge_cache_dir()
    yield
    purge_cache_dir()


@patch.dict(os.environ, {"KILI_API_KEY": "fake_key"})
def test_write_to_disk_without_permissions_not_crash(
    prepare_cache_dir, mocker: pytest_mock.MockerFixture
):
    """Test that we can still use kili even if we don't have write permissions."""
    mocker.patch("io.open", side_effect=PermissionError("No write permissions"))
    mocker.patch("os.mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch.object(Path, "mkdir", side_effect=PermissionError("No write permissions"))
    mocker.patch("kili.client.is_api_key_valid", return_value=True)
    mocker.patch.object(ApiKeyUseCases, "check_expiry_of_key_is_close")

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


@patch.dict(os.environ, {"KILI_API_KEY": "fake_key"})
def test_given_an_api_key_close_to_expiration_when_I_check_expiry_of_key_is_close_then_it_outputs_a_warning(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch("kili.client.is_api_key_valid", return_value=True)
    mocker.patch.object(GraphQLClient, "_initizalize_graphql_client")
    mocker.patch.object(
        KiliAPIGateway, "get_api_key_expiry_date", return_value=datetime.now() + timedelta(days=20)
    )

    # Then
    with pytest.warns(UserWarning, match="Your api key will be deprecated on"):
        # When
        _ = Kili()


@patch.dict(os.environ, {"KILI_API_KEY": "fake_key"})
def test_given_an_api_key_away_to_expiration_when_I_check_expiry_of_key_is_not_close_then_it_does_not_output_anything(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch("kili.client.is_api_key_valid", return_value=True)
    mocker.patch.object(GraphQLClient, "_initizalize_graphql_client")
    mocker.patch.object(
        KiliAPIGateway, "get_api_key_expiry_date", return_value=datetime.now() + timedelta(days=40)
    )

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        _ = Kili()
