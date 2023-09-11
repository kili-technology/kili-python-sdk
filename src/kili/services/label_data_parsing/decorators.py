"""Decorators for label response module."""

from typing import Callable, Tuple


def for_all_properties(decorator: Callable, exclude: Tuple[str, ...] = ()) -> Callable:
    """Class decorator to decorate all the properties of the decorated class.

    Decorates with a decorator passed as argument.

    Args:
        decorator: Decorator to apply to all the properties of the decorated class.
        exclude: Sequence of properties to exclude from the decoration.
    """

    def decorate(cls):
        for attr in dir(cls):
            if attr in exclude:
                continue
            if isinstance(getattr(cls, attr), property):
                setattr(
                    cls,
                    attr,
                    property(
                        decorator(getattr(cls, attr).fget),
                        decorator(getattr(cls, attr).fset),
                        decorator(getattr(cls, attr).fdel),
                        getattr(cls, attr).__doc__,
                    ),
                )
        return cls

    return decorate
