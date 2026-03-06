from collections.abc import Generator

import pytest
from typeguard import check_type

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.user import UserClientMethods
from kili.use_cases.user import UserUseCases


@pytest.mark.parametrize(
    ("args", "kwargs", "expected_return_type"),
    [
        ((), {}, list[dict]),
        ((), {"as_generator": True}, Generator[dict, None, None]),
        ((), {"as_generator": False}, list[dict]),
        ((), {"email": "test@kili.com", "as_generator": False}, list[dict]),
    ],
)
def test_given_users_query_when_i_call_it_i_get_correct_return_type(
    kili_api_gateway: KiliAPIGateway, mocker, args, kwargs, expected_return_type
):
    # Given
    mocker.patch.object(
        UserUseCases,
        "list_users",
        return_value=(u for u in [{"id": "fake_user_id_1"}, {"id": "fake_user_id_2"}]),
    )
    kili = UserClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    result = kili.users(*args, **kwargs)

    # Then
    check_type(result, expected_return_type)
    assert list(result) == [{"id": "fake_user_id_1"}, {"id": "fake_user_id_2"}]
