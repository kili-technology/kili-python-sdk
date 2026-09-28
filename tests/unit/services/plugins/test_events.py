# pylint: disable=missing-function-docstring,missing-class-docstring
import logging
from unittest.mock import MagicMock

import pytest
from kili_events import (
    AssetIssueCreatedEvent,
    AssetIssueEvent,
    AssetSkippedEvent,
    KiliEvent,
    LabelWorkflowRejectedEvent,
)

from kili.client import Kili
from kili.plugins import PluginCore, on_kili_event
from kili.services.plugins.events import subscribed_methods

SKIPPED = {
    "event": "asset.skipped",
    "organizationId": "organization_id",
    "projectId": "project_id",
    "userId": "user_id",
    "payload": {"assetId": "asset_id", "externalId": None, "skipped": True, "status": "TODO"},
}


class PluginHandler(PluginCore):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(kili=MagicMock(spec=Kili), project_id="project_id", logger=logger)
        self.received: list[tuple[str, KiliEvent]] = []

    @on_kili_event(AssetSkippedEvent)
    def on_skip(self, event: AssetSkippedEvent) -> None:
        self.received.append(("on_skip", event))

    @on_kili_event("asset.*")
    def on_any_asset_event(self, event: KiliEvent) -> None:
        self.received.append(("on_any_asset_event", event))

    @on_kili_event(AssetIssueEvent, LabelWorkflowRejectedEvent)
    def on_issue_or_rejection(self, event: KiliEvent) -> None:
        self.received.append(("on_issue_or_rejection", event))


def test_on_kili_event_records_the_patterns_of_models_families_and_strings():
    assert subscribed_methods(PluginHandler) == {
        "on_any_asset_event": ("asset.*",),
        "on_issue_or_rejection": (
            "asset.issue.cancelled",
            "asset.issue.created",
            "asset.issue.resolved",
            "label.workflow.rejected",
        ),
        "on_skip": ("asset.skipped",),
    }


def test_on_event_calls_every_method_subscribed_with_the_typed_event():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload=SKIPPED)

    assert [name for name, _ in plugin.received] == ["on_any_asset_event", "on_skip"]
    event = plugin.received[1][1]
    assert isinstance(event, AssetSkippedEvent)
    assert event.user_id == "user_id"
    assert event.payload.asset_id == "asset_id"


def test_on_event_calls_a_family_subscription_with_any_event_of_the_family():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(
        payload={
            "event": "asset.issue.created",
            "organizationId": "organization_id",
            "projectId": "project_id",
            "userId": "user_id",
            "payload": {"issueId": "issue_id", "assetId": "asset_id", "externalId": None},
        }
    )

    assert [name for name, _ in plugin.received] == ["on_any_asset_event", "on_issue_or_rejection"]
    assert isinstance(plugin.received[1][1], AssetIssueCreatedEvent)


def test_on_event_warns_when_no_method_subscribes_to_the_event():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload={**SKIPPED, "event": "project.archived"})

    assert plugin.received == []
    message = logger.warning.call_args.args[0]
    assert "'project.archived'" in message
    assert "on_skip" in message


def test_on_event_ignores_an_event_its_kili_events_does_not_know():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload={**SKIPPED, "event": "asset.teleported"})

    assert plugin.received == []
    assert "'asset.teleported'" in logger.warning.call_args.args[0]


def test_on_event_of_a_plugin_without_subscription_warns():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginCore(kili=MagicMock(spec=Kili), project_id="project_id", logger=logger)

    plugin.on_event(payload=SKIPPED)

    assert "subscriptions: none" in logger.warning.call_args.args[0]


def test_on_kili_event_needs_an_event():
    with pytest.raises(TypeError, match="needs the events to receive"):
        on_kili_event()


@pytest.mark.parametrize("event", [KiliEvent, dict, 3], ids=["KiliEvent", "dict", "int"])
def test_on_kili_event_rejects_what_is_no_event(event):
    with pytest.raises(TypeError, match="takes kili_events models"):
        on_kili_event(event)


def test_on_kili_event_rejects_a_malformed_pattern():
    with pytest.raises(ValueError, match="Invalid event pattern 'asset.>'"):
        on_kili_event("asset.>")
