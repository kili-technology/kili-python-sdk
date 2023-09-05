import warnings
from datetime import datetime, timedelta

import pytest
import pytest_mock

from kili.client import Kili
from kili.core.graphql.operations.api_key.queries import APIKeyQuery


def test_given_an_api_key_close_to_expiration_when_I_check_expiry_of_key_is_close_then_it_outputs_a_warning(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    expiry_date = datetime.now() + timedelta(days=20)

    api_key_query = mocker.MagicMock(
        spec=APIKeyQuery,
        return_value=iter(
            [{"expiryDate": datetime.strftime(expiry_date, r"%Y-%m-%dT%H:%M:%S.%fZ")}]
        ),
    )

    # Then
    with pytest.warns(UserWarning, match="Your api key will be deprecated on"):
        # When
        Kili._check_expiry_of_key_is_close(api_key_query, "dummy_api_key")


def test_given_an_api_key_away_to_expiration_when_I_check_expiry_of_key_is_close_then_it_does_not_output_anything(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    expiry_date = datetime.now() + timedelta(days=40)

    api_key_query = mocker.MagicMock(
        spec=APIKeyQuery,
        return_value=iter(
            [{"expiryDate": datetime.strftime(expiry_date, r"%Y-%m-%dT%H:%M:%S.%fZ")}]
        ),
    )

    # Then
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # checks that no warning is raised
        # When
        Kili._check_expiry_of_key_is_close(api_key_query, "dummy_api_key")
