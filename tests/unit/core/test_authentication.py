import datetime
import platform
import warnings
from unittest.mock import patch

import pytest
import pytest_mock

from kili.client import Kili
from kili.core.graphql.graphql_client import GraphQLClientName
from kili.core.graphql.operations.api_key.queries import APIKeyQuery


@pytest.mark.skipif(platform.system() == "Windows", reason="Does not work on Windows")
def test__check_expiry_of_key_is_close(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(Kili, "_check_api_key_valid", return_value=True)
    mocker.patch.object(Kili, "get_user", return_value={"id": "id", "email": "email"})
    mocker.patch("kili.client.GraphQLClient")

    with patch.object(
        APIKeyQuery, "__call__", return_value=iter([{"expiryDate": "2021-01-01T00:00:00.000Z"}])
    ):
        with pytest.warns(UserWarning, match="Your api key will be deprecated on"):
            _ = Kili(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)

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
            _ = Kili(api_key="", api_endpoint="", client_name=GraphQLClientName.SDK)
