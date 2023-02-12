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
            auth = KiliAuth(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)
