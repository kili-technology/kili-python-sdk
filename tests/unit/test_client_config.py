import json
import os
import tempfile
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kili.client import Kili
from kili.client_domain import Kili as KiliDomain
from kili.core.graphql.graphql_client import GraphQLClientName
from kili.domain_api import PluginsNamespace


@pytest.fixture()
def mock_http_operations():
    with (
        patch("kili.client.is_api_key_valid", return_value=True),
        patch("kili.client.HttpClient"),
        patch("kili.client.GraphQLClient") as mock_graphql_client,
        patch("kili.client.KiliAPIGateway") as mock_gateway,
    ):
        mock_gateway_instance = MagicMock()
        mock_gateway.return_value = mock_gateway_instance

        with patch("kili.use_cases.api_key.ApiKeyUseCases.check_expiry_of_key_is_close"):
            yield mock_graphql_client


def test_config_priority_method_over_env(mock_http_operations):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "kili-sdk-config.json"
        config_data = {"api_key": "file_key", "api_endpoint": "https://file.com"}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ["KILI_API_KEY"] = "env_key"
            os.environ["KILI_API_ENDPOINT"] = "https://env.com"

            kili = Kili(api_key="method_key", api_endpoint="https://method.com")

            assert kili.api_key == "method_key"
            assert kili.api_endpoint == "https://method.com"
        finally:
            os.chdir(original_cwd)
            os.environ.pop("KILI_API_KEY", None)
            os.environ.pop("KILI_API_ENDPOINT", None)


def test_config_priority_env_over_file(mock_http_operations):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "kili-sdk-config.json"
        config_data = {"api_key": "file_key", "api_endpoint": "https://file.com"}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ["KILI_API_KEY"] = "env_key"
            os.environ["KILI_API_ENDPOINT"] = "https://env.com"

            kili = Kili()

            assert kili.api_key == "env_key"
            assert kili.api_endpoint == "https://env.com"
        finally:
            os.chdir(original_cwd)
            os.environ.pop("KILI_API_KEY", None)
            os.environ.pop("KILI_API_ENDPOINT", None)


def test_config_file_used_when_no_env(mock_http_operations):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "kili-sdk-config.json"
        config_data = {"api_key": "file_key", "api_endpoint": "https://file.com"}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ.pop("KILI_API_KEY", None)
            os.environ.pop("KILI_API_ENDPOINT", None)

            kili = Kili()

            assert kili.api_key == "file_key"
            assert kili.api_endpoint == "https://file.com"
        finally:
            os.chdir(original_cwd)


def test_config_verify_priority(mock_http_operations):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "kili-sdk-config.json"
        config_data = {"api_key": "file_key", "verify_ssl": False}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ.pop("KILI_VERIFY", None)

            kili = Kili(verify=True)
            assert kili.verify is True

            kili2 = Kili()
            assert kili2.verify is False
        finally:
            os.chdir(original_cwd)


def test_config_verify_env_over_file(mock_http_operations):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "kili-sdk-config.json"
        config_data = {"api_key": "file_key", "verify_ssl": True}
        config_path.write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ["KILI_VERIFY"] = "false"

            kili = Kili()
            assert kili.verify is False
        finally:
            os.chdir(original_cwd)
            os.environ.pop("KILI_VERIFY", None)


def test_legacy_client_built_directly_is_deprecated(mock_http_operations):
    with pytest.warns(DeprecationWarning, match="from kili.client_domain import Kili") as record:
        Kili(api_key="key", api_endpoint="https://endpoint.com")

    assert record[0].filename == __file__  # the user's line, not kili's


@pytest.mark.parametrize(
    "build",
    [
        lambda: Kili(
            api_key="key", api_endpoint="https://endpoint.com", client_name=GraphQLClientName.CLI
        ),
        lambda: KiliDomain(api_key="key", api_endpoint="https://endpoint.com"),
    ],
    ids=["cli", "domain"],
)
def test_clients_the_sdk_builds_itself_do_not_warn(mock_http_operations, build):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        build()


def test_domain_client_exposes_plugins_llm_and_events(mock_http_operations):
    kili = KiliDomain(api_key="key", api_endpoint="https://endpoint.com")

    assert isinstance(kili.plugins, PluginsNamespace)
    assert kili.llm is kili.legacy_client.llm
    assert kili.events is kili.legacy_client.events


def test_domain_client_exposes_its_api_endpoint(mock_http_operations):
    kili = KiliDomain(api_key="key", api_endpoint="https://endpoint.com/api/label/v2/graphql")

    assert kili.api_endpoint == "https://endpoint.com/api/label/v2/graphql"


@pytest.mark.parametrize(
    ("argument", "env", "config", "expected"),
    [
        (None, None, None, False),
        (None, None, True, True),
        (None, "true", False, True),
        (None, "0", True, False),
        (False, "true", True, False),
        (True, None, None, True),
    ],
)
def test_config_disable_request_compression_priority(
    mock_http_operations, argument, env, config, expected
):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_data = {"api_key": "file_key"}
        if config is not None:
            config_data["disable_request_compression"] = config
        (Path(tmpdir) / "kili-sdk-config.json").write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ.pop("KILI_DISABLE_REQUEST_COMPRESSION", None)
            if env is not None:
                os.environ["KILI_DISABLE_REQUEST_COMPRESSION"] = env

            kili = Kili(disable_request_compression=argument)

            assert kili.disable_request_compression is expected
            graphql_client_kwargs = mock_http_operations.call_args.kwargs
            assert graphql_client_kwargs["disable_request_compression"] is expected
        finally:
            os.chdir(original_cwd)
            os.environ.pop("KILI_DISABLE_REQUEST_COMPRESSION", None)


@pytest.mark.parametrize(
    ("argument", "env", "config", "expected"),
    [
        (None, None, None, None),  # each function then uses its own default
        (None, None, True, True),
        (None, "yes", False, True),
        (None, "false", True, False),
        (True, "false", False, True),
    ],
)
def test_config_disable_tqdm_priority(mock_http_operations, argument, env, config, expected):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_data = {"api_key": "file_key"}
        if config is not None:
            config_data["disable_tqdm"] = config
        (Path(tmpdir) / "kili-sdk-config.json").write_text(json.dumps(config_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            os.environ.pop("KILI_DISABLE_TQDM", None)
            if env is not None:
                os.environ["KILI_DISABLE_TQDM"] = env

            kili = Kili(disable_tqdm=argument)

            assert kili.disable_tqdm is expected
        finally:
            os.chdir(original_cwd)
            os.environ.pop("KILI_DISABLE_TQDM", None)
