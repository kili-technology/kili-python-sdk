"""Tests for the asynchronous import verification poll.

`verify_batch_imported` reads notifications through the API gateway rather than through a
client method. These tests exercise the real gateway and fake only the transport, so a
regression in the filter, the requested fields or the pagination options is caught here.
"""

import re
from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.project import ProjectId
from kili.services.asset_import.base import BaseBatchImporter, BatchParams, ProjectParams
from kili.services.asset_import.exceptions import BatchImportError


def build_importer(notification_status: str):
    """Build an importer backed by a real gateway, recording every operation sent."""
    issued = []

    def execute(query, variables=None, **_kwargs):
        match = re.search(r"(?:query|mutation)\s+(\w+)", query)
        operation = match.group(1) if match else query
        issued.append((operation, query, variables))
        if operation == "countNotifications":
            return {"data": 1}
        return {"data": [{"status": notification_status}]}

    graphql_client = MagicMock()
    graphql_client.execute = MagicMock(side_effect=execute)
    kili = MagicMock()
    kili.kili_api_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=MagicMock())
    importer = BaseBatchImporter(
        kili,
        ProjectParams(project_id=ProjectId("project_id"), input_type="VIDEO"),
        BatchParams(is_asynchronous=True, is_hosted=False),
        MagicMock(),
    )
    return importer, issued


def test_given_a_successful_notification_when_verifying_then_it_filters_on_the_notification_id():
    # Given
    importer, issued = build_importer("SUCCESS")

    # When
    importer.verify_batch_imported("notification_id")

    # Then
    operations = [operation for operation, _, _ in issued]
    assert operations == ["countNotifications", "notifications"]

    _, notifications_query, notifications_variables = issued[1]
    assert notifications_variables == {
        "where": {"id": "notification_id"},
        "first": 1,
        "skip": 0,
    }
    assert "status" in notifications_query


def test_given_a_successful_notification_when_verifying_then_it_only_requests_the_status_field():
    # Given
    importer, issued = build_importer("SUCCESS")

    # When
    importer.verify_batch_imported("notification_id")

    # Then
    _, notifications_query, _ = issued[1]
    requested_fields = re.findall(r"^\s*(\w+)\s*$", notifications_query, flags=re.MULTILINE)
    assert requested_fields == ["status"]


def test_given_a_failed_notification_when_verifying_then_it_raises_a_batch_import_error():
    # Given
    importer, _ = build_importer("FAILURE")

    # When / Then
    with pytest.raises(BatchImportError):
        importer.verify_batch_imported("notification_id")
