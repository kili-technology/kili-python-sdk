"""Subscribe the methods of a plugin to Kili events, received as kili-events models."""

import inspect
import types
import typing
from collections.abc import Callable
from typing import Any, TypeVar, Union

from kili_events import EVENT_MODELS, KiliEvent, is_system_event

# Where @on_kili_event records the models a method receives, read back when an event arrives.
SUBSCRIPTION_ATTRIBUTE = "__kili_event_models__"

_Method = TypeVar("_Method", bound=Callable[..., Any])

_EXAMPLE = "def on_skip(self, event: AssetSkippedEvent)"


def event_models(annotation: object) -> tuple[type[KiliEvent], ...]:
    """Return the kili_events models an annotation of the event parameter stands for.

    Args:
        annotation: A kili_events model (`AssetSkippedEvent`), a family of them
            (`AssetWorkflowEvent`), or a union of models and families
            (`AssetWorkflowEvent | LabelWorkflowEvent`).

    Returns:
        The models.

    Raises:
        TypeError: The annotation is none of these.
    """
    if typing.get_origin(annotation) in (Union, types.UnionType):
        members = typing.get_args(annotation)
    else:
        members = (annotation,)
    known = set(EVENT_MODELS.values())
    models = tuple(member for member in dict.fromkeys(members) if member in known)
    if len(models) == len(set(members)):
        return models
    raise TypeError(
        "The event parameter is annotated with kili_events models (AssetSkippedEvent), families"
        " of events (AssetWorkflowEvent) or a union of them (AssetWorkflowEvent |"
        f" LabelWorkflowEvent), not {annotation!r}."
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


def on_kili_event(method: _Method, /) -> _Method:
    """Call the decorated method of a plugin with each event its parameter's annotation names.

    The annotation of the event parameter is the subscription: a kili_events model
    (`AssetSkippedEvent`), a family of events (`AssetWorkflowEvent`: every `asset.workflow.…`
    event), or a union of them (`AssetWorkflowEvent | LabelWorkflowEvent`). The method receives
    each of these events, parsed into its model. When the plugin is uploaded, Kili is told to
    send it the events of every decorated method.

    The decorator takes no arguments.

    Args:
        method: A plain method taking `self` and the event.

    Returns:
        The method.

    Raises:
        TypeError: An argument given to the decorator, an async method, a method that does not
            take `self` and the event, or an event parameter that is not annotated with
            kili_events models or families.

    !!! example
        ```python
        from kili_events import AssetSkippedEvent, AssetWorkflowEvent, LabelWorkflowEvent

        from kili.plugins import PluginCore, on_kili_event


        class PluginHandler(PluginCore):
            @on_kili_event
            def on_skip(self, event: AssetSkippedEvent) -> None:
                self.logger.info(f"Asset {event.payload.asset_id} skipped by {event.user_id}")

            @on_kili_event
            def on_workflow(self, event: AssetWorkflowEvent | LabelWorkflowEvent) -> None:
                self.logger.info(f"Received {event.event}")
        ```
    """
    setattr(method, SUBSCRIPTION_ATTRIBUTE, _subscription(method))
    return method


def _subscription(method: object) -> tuple[type[KiliEvent], ...]:
    """The models a method decorated with @on_kili_event receives, read from its annotation."""
    if not inspect.isfunction(method):
        raise TypeError(
            f"@on_kili_event takes no arguments, not {method!r}: annotate the event parameter of"
            f" the method with the events to receive, e.g. `{_EXAMPLE}`."
        )
    name = method.__name__
    if inspect.iscoroutinefunction(method):
        raise TypeError(
            f"@on_kili_event decorates plain methods: {name} is async, and a plugin would never"
            " await it."
        )
    parameters = list(inspect.signature(method).parameters.values())
    if len(parameters) != 2 or any(
        parameter.kind not in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
        for parameter in parameters
    ):
        raise TypeError(f"{name} takes self and the event, e.g. `{_EXAMPLE}`.")
    event = parameters[1].name
    if event not in method.__annotations__:
        raise TypeError(
            f"{name}: annotate the event parameter with the events to receive, e.g. `{_EXAMPLE}`."
        )
    # The event's annotation alone: the others (self, the return) are none of the plugin's
    # subscription, and may name what is not bound yet. Not the method itself either, whose
    # `= None` default would turn the annotation into an Optional on Python 3.10.
    only_event = types.SimpleNamespace(__annotations__={event: method.__annotations__[event]})
    try:
        annotation = typing.get_type_hints(
            only_event, globalns=inspect.unwrap(method).__globals__, include_extras=True
        )[event]
    except NameError as error:
        raise TypeError(
            f"{name}: the annotation of the event cannot be resolved: {error}."
        ) from error
    try:
        return event_models(annotation)
    except TypeError as error:
        raise TypeError(f"{name}: {error}") from error


def subscribed_methods(plugin_class: type) -> dict[str, tuple[type[KiliEvent], ...]]:
    """Return the methods of a plugin class decorated with `@on_kili_event`, and their models."""
    return {
        name: getattr(method, SUBSCRIPTION_ATTRIBUTE)
        for name, method in inspect.getmembers(plugin_class, inspect.isfunction)
        if hasattr(method, SUBSCRIPTION_ATTRIBUTE)
    }
