# pylint: disable=missing-function-docstring,missing-class-docstring
import logging
from typing import Annotated, Optional, Union, get_args
from unittest.mock import MagicMock

import pytest
from kili_events import (
    AnyEvent,
    AssetIssueCreatedEvent,
    AssetIssueEvent,
    AssetSkippedEvent,
    KiliEvent,
    LabelWorkflowEvent,
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

ISSUE_CREATED = {
    "event": "asset.issue.created",
    "organizationId": "organization_id",
    "projectId": "project_id",
    "userId": "user_id",
    "payload": {"issueId": "issue_id", "assetId": "asset_id", "externalId": None},
}


class PluginHandler(PluginCore):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(kili=MagicMock(spec=Kili), project_id="project_id", logger=logger)
        self.received: list[tuple[str, KiliEvent]] = []

    @on_kili_event
    def on_skip(self, event: AssetSkippedEvent) -> None:
        self.received.append(("on_skip", event))

    @on_kili_event
    def on_any_event(self, event: AnyEvent) -> None:
        self.received.append(("on_any_event", event))

    @on_kili_event
    def on_issue_or_rejection(self, event: AssetIssueEvent | LabelWorkflowRejectedEvent) -> None:
        self.received.append(("on_issue_or_rejection", event))


def test_on_kili_event_records_the_models_of_the_annotation():
    subscriptions = subscribed_methods(PluginHandler)

    assert subscriptions["on_skip"] == (AssetSkippedEvent,)
    assert set(subscriptions["on_issue_or_rejection"]) == {
        *get_args(AssetIssueEvent),
        LabelWorkflowRejectedEvent,
    }
    assert len(subscriptions["on_any_event"]) == len(get_args(AnyEvent))


def test_on_kili_event_reads_annotations_postponed_by_future_import():
    namespace: dict = {}
    exec(  # pylint: disable=exec-used
        "from __future__ import annotations\n"
        "from typing import Union\n"
        "from kili_events import AssetSkippedEvent, LabelWorkflowEvent\n"
        "from kili.plugins import PluginCore, on_kili_event\n"
        "class PluginHandler(PluginCore):\n"
        "    @on_kili_event\n"
        "    def on_skip(self, event: Union[AssetSkippedEvent, LabelWorkflowEvent]) -> None:\n"
        "        pass\n",
        namespace,
    )

    assert subscribed_methods(namespace["PluginHandler"])["on_skip"] == (
        AssetSkippedEvent,
        *get_args(LabelWorkflowEvent),
    )


def test_on_event_calls_every_method_whose_annotation_the_event_is_an_instance_of():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload=SKIPPED)

    assert [name for name, _ in plugin.received] == ["on_any_event", "on_skip"]
    event = plugin.received[1][1]
    assert isinstance(event, AssetSkippedEvent)
    assert event.user_id == "user_id"
    assert event.payload.asset_id == "asset_id"


def test_on_event_calls_a_family_method_with_any_event_of_the_family():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload=ISSUE_CREATED)

    assert [name for name, _ in plugin.received] == ["on_any_event", "on_issue_or_rejection"]
    assert isinstance(plugin.received[1][1], AssetIssueCreatedEvent)


def test_on_event_warns_when_no_method_receives_the_event():
    class SkipOnly(PluginCore):
        @on_kili_event
        def on_skip(self, event: AssetSkippedEvent) -> None:
            pass

    logger = MagicMock(spec=logging.Logger)
    plugin = SkipOnly(kili=MagicMock(spec=Kili), project_id="project_id", logger=logger)

    plugin.on_event(payload=ISSUE_CREATED)

    message = logger.warning.call_args.args[0]
    assert "'asset.issue.created'" in message
    assert "on_skip" in message


def test_on_event_ignores_an_event_its_kili_events_does_not_know():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginHandler(logger)

    plugin.on_event(payload={**SKIPPED, "event": "asset.teleported"})

    assert plugin.received == []
    assert "'asset.teleported'" in logger.warning.call_args.args[0]


def test_on_event_of_a_plugin_without_decorated_method_warns():
    logger = MagicMock(spec=logging.Logger)
    plugin = PluginCore(kili=MagicMock(spec=Kili), project_id="project_id", logger=logger)

    plugin.on_event(payload=SKIPPED)

    assert "@on_kili_event: none" in logger.warning.call_args.args[0]


@pytest.mark.parametrize(
    "argument", [AssetSkippedEvent, "asset.skipped"], ids=["a model", "a pattern"]
)
def test_on_kili_event_takes_no_arguments(argument):
    with pytest.raises(TypeError, match="@on_kili_event takes no arguments"):
        on_kili_event(argument)  # pyright: ignore[reportGeneralTypeIssues,reportArgumentType]


def test_on_kili_event_with_parentheses_is_refused():
    with pytest.raises(TypeError):
        on_kili_event()  # pyright: ignore[reportCallIssue]


@pytest.mark.parametrize(
    "annotation",
    [
        KiliEvent,
        dict,
        Optional[AssetSkippedEvent],
        Union[AssetSkippedEvent, str],
        Annotated[AssetSkippedEvent, "metadata"],
    ],
    ids=["KiliEvent", "dict", "Optional", "a union with str", "Annotated"],
)
def test_on_kili_event_refuses_an_annotation_that_is_no_event(annotation):
    def on_something(self, event):
        pass

    on_something.__annotations__ = {"event": annotation}

    with pytest.raises(TypeError, match="on_something: The event parameter is annotated with"):
        on_kili_event(on_something)


def test_on_kili_event_refuses_a_parameter_without_annotation():
    with pytest.raises(TypeError, match="on_skip: annotate the event parameter"):

        @on_kili_event
        def on_skip(self, event):
            pass


@pytest.mark.parametrize(
    "signature",
    ["self", "self, event: AssetSkippedEvent, other", "self, *events: AssetSkippedEvent"],
    ids=["no event", "two parameters", "varargs"],
)
def test_on_kili_event_refuses_a_method_that_does_not_take_self_and_the_event(signature):
    namespace = {"AssetSkippedEvent": AssetSkippedEvent}
    exec(f"def on_skip({signature}):\n    pass\n", namespace)  # pylint: disable=exec-used

    with pytest.raises(TypeError, match="on_skip takes self and the event"):
        on_kili_event(namespace["on_skip"])


def test_on_kili_event_names_an_annotation_it_cannot_resolve():
    def on_skip(self, event: "NotImported"):  # type: ignore[name-defined]  # noqa: F821
        pass

    with pytest.raises(TypeError, match="on_skip: the annotation of the event cannot be resolved"):
        on_kili_event(on_skip)


def test_on_kili_event_refuses_an_async_method():
    with pytest.raises(TypeError, match="on_skip is async"):

        @on_kili_event
        async def on_skip(self, event: AssetSkippedEvent):
            pass


def test_a_union_of_families_flattens_into_their_models():
    @on_kili_event
    def on_workflow(self, event: AssetIssueEvent | LabelWorkflowEvent) -> None:
        pass

    class Plugin(PluginCore):
        handler = on_workflow

    assert subscribed_methods(Plugin)["handler"] == (
        *get_args(AssetIssueEvent),
        *get_args(LabelWorkflowEvent),
    )
