import datetime
import warnings
from unittest.mock import patch

import pytest

from kili.authentication import KiliAuth
from kili.graphql.graphql_client import GraphQLClientName


@patch("kili.authentication.requests")
@patch.object(KiliAuth, "check_versions_match", side_effect=Exception)
def test_warn_cant_check_kili_version(mocked_requests, mocked_check_versions_match):
    with pytest.raises(Exception):
        with pytest.warns(
            UserWarning, match="We could not check the version, there might be a version"
        ):
            _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)


@patch("kili.authentication.requests")
@patch.object(KiliAuth, "check_versions_match", return_value=True)
@patch.object(KiliAuth, "check_api_key_valid", return_value=True)
@patch("kili.authentication.GraphQLClient", return_value=None)
@patch("kili.authentication.APIKeyQuery.__call__")
def test_check_expiry_of_key_is_close(mocker_api_key_query, *_):
    mocker_api_key_query.return_value = yield {"createdAt": "2020-01-01T00:00:00.000Z"}
    with pytest.warns(UserWarning, match="Your api key will be deprecated on"):
        _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)

    mocker_api_key_query.return_value = yield {"createdAt": datetime.datetime.now().isoformat()}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _ = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)
