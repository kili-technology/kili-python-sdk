import datetime
import warnings
from unittest.mock import patch

import pytest

from kili.authentication import KiliAuth
from kili.graphql.graphql_client import GraphQLClientName
from kili.graphql.operations.api_key.queries import APIKeyQuery


@patch("kili.authentication.requests")
@patch.object(KiliAuth, "check_versions_match", side_effect=Exception)
@patch.object(KiliAuth, "check_api_key_valid", return_value=True)
@patch.object(KiliAuth, "check_expiry_of_key_is_close", return_value=True)
@patch.object(KiliAuth, "get_user", return_value={"id": "id", "email": "email"})
def test_warn_cant_check_kili_version(*_):
    message = (
        "We could not check the version, there might be a version"
        "mismatch or the app might be in deployment"
    )
    with pytest.warns(UserWarning, match=message):
        _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)


@patch("kili.authentication.requests")
@patch.object(KiliAuth, "check_versions_match", return_value=True)
@patch.object(KiliAuth, "check_api_key_valid", return_value=True)
@patch.object(KiliAuth, "get_user", return_value={"id": "id", "email": "email"})
@patch("kili.authentication.GraphQLClient", return_value=None)
def test_check_expiry_of_key_is_close(*_):
    with patch.object(
        APIKeyQuery, "__call__", return_value=iter([{"expiryDate": "2021-01-01T00:00:00.000Z"}])
    ):
        with pytest.warns(UserWarning, match="Your api key will be deprecated on"):
            _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)

    current = datetime.datetime.now()
    with patch.object(
        APIKeyQuery,
        "__call__",
        return_value=iter(
            [{"expiryDate": f"{current.year+1}-{current.month}-{current.day}T09:54:19.071Z"}]
        ),
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)
