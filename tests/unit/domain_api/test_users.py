"""Tests for the UsersNamespace."""

from unittest.mock import create_autospec

import pytest
from typeguard import TypeCheckError

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain_api.users import UsersNamespace
from kili.presentation.client.user import UserClientMethods

DEFAULT_FIELDS = ("email", "id", "firstname", "lastname")


class TestUsersNamespaceActivatedFilter:
    """The `activated` filter of list(), list_as_generator() and count()."""

    @pytest.fixture()
    def mock_client(self):
        """Create a client that refuses any argument the legacy methods do not take."""
        return create_autospec(UserClientMethods, instance=True)

    @pytest.fixture()
    def users_namespace(self, mock_client, mocker):
        """Create a UsersNamespace instance."""
        return UsersNamespace(mock_client, mocker.MagicMock(spec=KiliAPIGateway))

    @pytest.mark.parametrize("activated", [True, False, None])
    def test_list_forwards_activated(self, users_namespace, mock_client, activated):
        mock_client.users.return_value = [{"id": "user_1"}]

        result = users_namespace.list(filter={"activated": activated})

        mock_client.users.assert_called_once_with(
            as_generator=False,
            disable_tqdm=None,
            fields=DEFAULT_FIELDS,
            first=None,
            skip=0,
            activated=activated,
        )
        assert result == [{"id": "user_1"}]

    @pytest.mark.parametrize("activated", [True, False, None])
    def test_list_as_generator_forwards_activated(self, users_namespace, mock_client, activated):
        mock_client.users.return_value = (user for user in [{"id": "user_1"}])

        result = users_namespace.list_as_generator(filter={"activated": activated})

        mock_client.users.assert_called_once_with(
            as_generator=True,
            disable_tqdm=None,
            fields=DEFAULT_FIELDS,
            first=None,
            skip=0,
            activated=activated,
        )
        assert list(result) == [{"id": "user_1"}]

    @pytest.mark.parametrize("activated", [True, False, None])
    def test_count_forwards_activated(self, users_namespace, mock_client, activated):
        mock_client.count_users.return_value = 7

        result = users_namespace.count(filter={"activated": activated})

        mock_client.count_users.assert_called_once_with(activated=activated)
        assert result == 7

    def test_activated_combines_with_the_other_filters(self, users_namespace, mock_client):
        mock_client.users.return_value = []
        mock_client.count_users.return_value = 0
        filter_ = {"organization_id": "org_1", "email": "user@example.com", "activated": False}

        users_namespace.list(filter=filter_, first=5, skip=2)
        users_namespace.count(filter=filter_)

        mock_client.users.assert_called_once_with(
            as_generator=False,
            disable_tqdm=None,
            fields=DEFAULT_FIELDS,
            first=5,
            skip=2,
            organization_id="org_1",
            email="user@example.com",
            activated=False,
        )
        mock_client.count_users.assert_called_once_with(
            organization_id="org_1", email="user@example.com", activated=False
        )

    def test_without_the_option_everybody_is_asked_for(self, users_namespace, mock_client):
        mock_client.users.return_value = []
        mock_client.count_users.return_value = 0

        users_namespace.list()
        users_namespace.count()

        assert "activated" not in mock_client.users.call_args.kwargs
        mock_client.count_users.assert_called_once_with()

    @pytest.mark.parametrize("method", ["list", "list_as_generator", "count"])
    def test_a_non_boolean_activated_is_refused(self, users_namespace, mock_client, method):
        with pytest.raises(TypeCheckError):
            getattr(users_namespace, method)(filter={"activated": "yes"})

        mock_client.users.assert_not_called()
        mock_client.count_users.assert_not_called()
