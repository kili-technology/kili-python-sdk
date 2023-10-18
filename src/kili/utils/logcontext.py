"""Utils to log calls."""

import functools
import platform
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, List

from kili import __version__
from kili.core.graphql.clientnames import GraphQLClientName


class Singleton(type):
    """Utility meta-class to guarantee single instance."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class LogContext(Dict[str, str], metaclass=Singleton):
    # pylint: disable=line-too-long
    """Dict-like singleton that holds the data for the log context, to be passed to the request headers."""

    def __init__(self) -> None:
        self["kili-client-name"] = GraphQLClientName.SDK.value
        self["kili-client-version"] = __version__
        self["kili-client-language-name"] = "Python"
        self["kili-client-language-version"] = platform.python_version()
        self["kili-client-platform-version"] = platform.version()
        self["kili-client-platform-name"] = platform.system()


def for_all_methods(decorator: Callable, exclude: List[str]):
    """Class Decorator to decorate all the method with a decorator passed as argument."""

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def log_call(func: Callable):
    """Decorator to add call info to the client logging context."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context = LogContext()
        context["kili-client-method-name"] = func.__name__
        context["kili-client-call-time"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        context["kili-client-call-uuid"] = str(uuid.uuid4())
        return func(*args, **kwargs)

    return wrapper
