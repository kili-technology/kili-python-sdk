"""Subscribe the methods of a plugin to Kili events, received as kili-events models."""

import inspect
from collections.abc import Callable
from typing import Any, TypeVar, Union, get_args, get_origin

from kili_events import EVENT_MODELS, KiliEvent, events_matching, is_system_event

# Where @on_kili_event records the patterns of a method, read back when an event arrives.
SUBSCRIPTIONS_ATTRIBUTE = "__kili_event_patterns__"

_Method = TypeVar("_Method", bound=Callable[..., Any])


def event_patterns(event: object) -> tuple[str, ...]:
    """Return the patterns an argument of `@on_kili_event` subscribes to.

    Args:
        event: A kili_events model, a family of them, or a pattern.

    Returns:
        The model's subject, the subjects of the family's models, or the pattern.

    Raises:
        ValueError: The pattern is malformed.
        TypeError: The argument is none of the three.
    """
    if isinstance(event, str):
        events_matching(event)  # raises on a malformed pattern
        return (event,)
    if isinstance(event, type) and issubclass(event, KiliEvent) and event is not KiliEvent:
        return (event.subject(),)
    if get_origin(event) is Union:
        members = get_args(event)
        if all(isinstance(member, type) and issubclass(member, KiliEvent) for member in members):
            return tuple(member.subject() for member in members)
    raise TypeError(
        "@on_kili_event takes kili_events models (AssetSkippedEvent), families of events"
        f" (AssetWorkflowEvent) or patterns ('label.workflow.*'), not {event!r}."
    )


def plugin_receives(subject: str) -> bool:
    """Whether Kili sends an event to plugins: system events and events without project never.

    Args:
        subject: The event subject, e.g. "asset.skipped".

    Returns:
        False for a system event, or an event no project is attached to.
    """
    model = EVENT_MODELS.get(subject)
    return not is_system_event(subject) and (model is None or "project_id" in model.model_fields)


def on_kili_event(*events: object) -> Callable[[_Method], _Method]:
    """Call the decorated method of a plugin with each event it subscribes to.

    The method receives the event parsed into its kili_events model. When the plugin is
    uploaded, Kili is told to send it the events of every decorated method.

    Args:
        *events: The events to receive, any mix of:
            kili_events models (`AssetSkippedEvent`),
            families of events (`AssetWorkflowEvent`: every `asset.workflow.…` event),
            patterns, where `*` stands for one or more names (`"label.workflow.*"`).

    Returns:
        The decorator.

    Raises:
        TypeError: No event, an argument that is none of the three, or an async method.
        ValueError: A malformed pattern.

    !!! example
        ```python
        from kili_events import AssetSkippedEvent, AssetWorkflowEvent

        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event(AssetSkippedEvent)
            def on_skip(self, event: AssetSkippedEvent) -> None:
                self.logger.info(f"Asset {event.payload.asset_id} skipped by {event.user_id}")

            @on_kili_event(AssetWorkflowEvent, "label.workflow.*")
            def on_workflow(self, event) -> None:
                self.logger.info(f"Received {event.event}")
        ```
    """
    if not events:
        raise TypeError(
            "@on_kili_event needs the events to receive, e.g. @on_kili_event(AssetSkippedEvent)."
        )
    patterns = tuple(
        dict.fromkeys(pattern for event in events for pattern in event_patterns(event))
    )

    def decorator(method: _Method) -> _Method:
        if inspect.iscoroutinefunction(method):
            raise TypeError(
                f"@on_kili_event decorates plain methods: {method.__name__} is async, and a plugin"
                " would never await it."
            )
        setattr(method, SUBSCRIPTIONS_ATTRIBUTE, patterns)
        return method

    return decorator


def subscribed_methods(plugin_class: type) -> dict[str, tuple[str, ...]]:
    """Return the methods of a plugin class decorated with `@on_kili_event`, and their patterns."""
    return {
        name: getattr(method, SUBSCRIPTIONS_ATTRIBUTE)
        for name, method in inspect.getmembers(plugin_class, inspect.isfunction)
        if hasattr(method, SUBSCRIPTIONS_ATTRIBUTE)
    }
