import pytest_mock

from kili.presentation.client.notification import NotificationClientMethods
from kili.use_cases.notification import NotificationUseCases


def test_given_client_when_fetching_notifications_it_works(
    mocker: pytest_mock.MockerFixture, kili_api_gateway
):
    mocker.patch.object(
        NotificationUseCases, "list_notifications", return_value=(n for n in [{"id": "notif_id"}])
    )
    # Given
    kili = NotificationClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    notifs = kili.notifications()

    # Then
    assert notifs == [{"id": "notif_id"}]
