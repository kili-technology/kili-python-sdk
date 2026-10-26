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
            "kili.organizations.metrics() is deprecated and will be removed: use"
            " kili.organizations.usage() instead, which counts as the Usage and license page of the"
            " app does."
        ]
        assert result == metrics
        mock_client.organization_metrics.assert_called_once_with(
            organization_id="org_id",
            start_date=datetime(2022, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2022, 1, 5, tzinfo=timezone.utc),
            fields=("numberOfAnnotations", "numberOfHours", "numberOfLabeledAssets"),
        )

    def test_usage_calls_the_legacy_method(self, organizations_namespace, mock_client):
        """Usage() passes its arguments to organization_usage()."""
        # Given
        mock_client.organization_usage.return_value = [{"metric": "LABELED_ASSETS", "total": 3.0}]

        # When
        result = organizations_namespace.usage(metrics=["LABELED_ASSETS"], granularity="MONTH")

        # Then
        assert result == [{"metric": "LABELED_ASSETS", "total": 3.0}]
        mock_client.organization_usage.assert_called_once_with(
            metrics=["LABELED_ASSETS"],
            start_date=None,
            end_date=None,
            granularity="MONTH",
            project_id=None,
            organization_id=None,
        )

    @pytest.mark.parametrize(
        ("method", "as_generator"),
        [("usage_by_project", False), ("usage_by_project_as_generator", True)],
    )
    def test_usage_by_project_calls_the_legacy_method(
        self, organizations_namespace, mock_client, method, as_generator
    ):
        """usage_by_project() and its generator pass their arguments to organization_usage_by_project()."""
        # Given
        projects = [{"projectId": "project_id"}]
        mock_client.organization_usage_by_project.return_value = (
            (project for project in projects) if as_generator else projects
        )

        # When
        result = getattr(organizations_namespace, method)(search_query="shelves", first=5)

        # Then
        assert list(result) == projects
        mock_client.organization_usage_by_project.assert_called_once_with(
            metrics=(
                "LABELED_ASSETS",
                "NUMBER_OF_ANNOTATIONS",
                "ROOT_NUMBER_OF_ANNOTATIONS",
                "LABELING_TIME",
            ),
            start_date=None,
            end_date=None,
            search_query="shelves",
            organization_id=None,
            first=5,
            skip=0,
            disable_tqdm=None,
            as_generator=as_generator,
        )
