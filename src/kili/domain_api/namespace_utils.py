"""Utility functions for domain namespace introspection."""

import inspect
from functools import cached_property
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from typing import Any


def get_available_methods(instance: "Any") -> List[str]:
    """Get list of public methods for any namespace instance.

    This utility function dynamically discovers all public callable methods
    defined in an instance's class, excluding:
    - Private/protected methods (starting with _)
    - Special methods (like __init__, __call__)
    - Properties and cached_properties
    - Methods inherited from parent classes (not defined in instance.__class__.__dict__)

    Args:
        instance: Any namespace instance to inspect

    Returns:
        Sorted list of public method names available on this instance

    Example:
        >>> from kili.domain_api.namespace_utils import get_available_methods
        >>> from kili.client_domain import Kili
        >>> kili = Kili()
        >>> methods = get_available_methods(kili.assets)
        >>> print(methods)  # ['append_to_roles', 'count', 'create', ...]
    """
    methods = []
    target_class = instance.__class__

    for name, member in inspect.getmembers(instance):
        # Skip private/protected methods
        if name.startswith("_"):
            continue

        # Skip if it's a property or cached_property
        try:
            class_attr = inspect.getattr_static(target_class, name, None)
            if isinstance(class_attr, (property, cached_property)):
                continue
        except AttributeError:
            continue

        # Only include callable methods defined in this class
        if callable(member) and name in target_class.__dict__:
            methods.append(name)

    return sorted(methods)
