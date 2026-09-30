"""Tests for the ProjectsNamespace."""

from unittest.mock import Mock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili as KiliLegacy
from kili.domain_api.projects import ProjectsNamespace


class TestProjectsNamespaceAuthor:
    """Tests for the projects of an author and their hand-over."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        return Mock(spec=KiliLegacy)

    @pytest.fixture()
    def projects_namespace(self, mock_client):
        """Create a ProjectsNamespace instance."""
        return ProjectsNamespace(mock_client, Mock(spec=KiliAPIGateway))

    def test_list_passes_the_author_to_the_legacy_method(self, projects_namespace, mock_client):
        mock_client.projects.return_value = []

        result = projects_namespace.list(filter={"author_id": "colleague_id", "archived": False})

        assert result == []
        kwargs = mock_client.projects.call_args.kwargs
        assert kwargs["author_id"] == "colleague_id"
        assert kwargs["archived"] is False
        assert kwargs["as_generator"] is False

    def test_list_as_generator_passes_the_author_to_the_legacy_method(
        self, projects_namespace, mock_client
    ):
        mock_client.projects.return_value = (project for project in [])

        projects_namespace.list_as_generator(filter={"author_id": "colleague_id"})

        assert mock_client.projects.call_args.kwargs["author_id"] == "colleague_id"

    def test_count_passes_the_author_to_the_legacy_method(self, projects_namespace, mock_client):
        mock_client.count_projects.return_value = 0

        result = projects_namespace.count(filter={"author_id": "colleague_id"})

        assert result == 0
        mock_client.count_projects.assert_called_once_with(author_id="colleague_id")

    def test_transfer_authorship_calls_the_legacy_method(self, projects_namespace, mock_client):
        mock_client.transfer_projects_authorship.return_value = {
            "transferred": ["p1"],
            "failed": [{"id": "p2", "error": "not an admin"}],
        }

        result = projects_namespace.transfer_authorship(
            author_id="former_author_id", new_author_id="new_author_id"
        )

        mock_client.transfer_projects_authorship.assert_called_once_with(
            author_id="former_author_id",
            new_author_id="new_author_id",
            author_email=None,
            new_author_email=None,
        )
        assert result["failed"] == [{"id": "p2", "error": "not an admin"}]

    def test_list_and_count_pass_the_author_email_to_the_legacy_method(
        self, projects_namespace, mock_client
    ):
        mock_client.projects.return_value = []
        mock_client.count_projects.return_value = 0

        projects_namespace.list(filter={"author_email": "jane@acme.com"})
        projects_namespace.count(filter={"author_email": "jane@acme.com"})

        assert mock_client.projects.call_args.kwargs["author_email"] == "jane@acme.com"
        mock_client.count_projects.assert_called_once_with(author_email="jane@acme.com")

    def test_transfer_authorship_passes_the_emails_to_the_legacy_method(
        self, projects_namespace, mock_client
    ):
        mock_client.transfer_projects_authorship.return_value = {"transferred": [], "failed": []}

        projects_namespace.transfer_authorship(
            author_email="leaving@acme.com", new_author_email="new@acme.com"
        )

        mock_client.transfer_projects_authorship.assert_called_once_with(
            author_id=None,
            new_author_id=None,
            author_email="leaving@acme.com",
            new_author_email="new@acme.com",
        )
