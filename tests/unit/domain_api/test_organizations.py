"""Tests for the OrganizationsNamespace."""

import warnings
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.domain_api.organizations import OrganizationsNamespace
from kili.presentation.client.organization import ORGANIZATION_METRICS_DEPRECATION


class TestOrganizationsNamespace:
    """Tests for OrganizationsNamespace functionality."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        return Mock(spec=Kili)

    @pytest.fixture()
    def organizations_namespace(self, mock_client):
        """Create an OrganizationsNamespace instance."""
        return OrganizationsNamespace(mock_client, Mock(spec=KiliAPIGateway))

    def test_metrics_warns_once_that_it_is_deprecated(self, organizations_namespace, mock_client):
        """Metrics() warns in its own terms and silences the legacy method's warning."""
        # Given
        metrics = {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}

        def legacy_organization_metrics(**_):
            warnings.warn(ORGANIZATION_METRICS_DEPRECATION, DeprecationWarning, stacklevel=1)
            return metrics

        mock_client.organization_metrics.side_effect = legacy_organization_metrics

        # When
        with pytest.warns(DeprecationWarning) as records:
            result = organizations_namespace.metrics(
                organization_id="org_id",
                start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2022, 1, 5, tzinfo=timezone.utc),
            )

        # Then
        assert [str(record.message) for record in records] == [
            "kili.organizations.metrics() is deprecated and will be removed: it counts differently"
            " from the Usage and license page of the app, which is the reference for your"
            " consumption."
        ]
        assert result == metrics
        mock_client.organization_metrics.assert_called_once_with(
            organization_id="org_id",
            start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2022, 1, 5, tzinfo=timezone.utc),
            fields=("numberOfAnnotations", "numberOfHours", "numberOfLabeledAssets"),
        )
