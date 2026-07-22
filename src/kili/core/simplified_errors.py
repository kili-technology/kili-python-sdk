"""Opt-in simplified display of the SDK errors and warnings.

When error simplification is enabled, exceptions raised by the SDK are reported
as a single-line message (without traceback), backend GraphQL error messages are
stripped from their technical noise (error codes, stack traces, boilerplate),
and warnings emitted by the SDK are displayed on a single line.

It can be enabled with the ``KILI_SDK_SIMPLIFY_ERROR_LOGS`` environment variable
(set to ``true``, ``1`` or ``yes``), or with ``"simplify_error_logs": true`` in
the ``kili-sdk-config.json`` configuration file.
"""

import os
import re
import sys
import warnings
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Optional, Union

SIMPLIFY_ERROR_LOGS_ENV_VAR = "KILI_SDK_SIMPLIFY_ERROR_LOGS"
SIMPLIFY_ERROR_LOGS_CONFIG_KEY = "simplify_error_logs"

_TRUTHY_ENV_VALUES = ("true", "1", "yes")

# Backend GraphQL error messages look like:
# "[notFound] Resource not found. -- This can be due to: Project with id X not found"
_ERROR_CODE_PREFIX_REGEX = re.compile(r"^\[\w+\]\s*")
_CAUSE_SEPARATOR = " -- This can be due to: "
# Stack-trace lines that older backend versions embed in the error message.
_STACK_FRAME_LINE_REGEX = re.compile(r"^\s+at\s.*$", flags=re.MULTILINE)

_RED = "\033[91m"
_RESET = "\033[0m"

_default_formatwarning = warnings.formatwarning

_state: dict[str, Any] = {
    "enabled_from_config": False,
    "previous_excepthook": None,
    "previous_formatwarning": None,
}


def is_error_simplification_enabled() -> bool:
    """Return whether the simplified error display is currently enabled.

    The ``KILI_SDK_SIMPLIFY_ERROR_LOGS`` environment variable takes precedence
    over the configuration file.
    """
    env_flag = _env_flag_value()
    if env_flag is not None:
        return env_flag
    return _state["enabled_from_config"]


def enable_error_simplification_from_config(config: Mapping[str, Any]) -> None:
    """Enable the simplified error display if the configuration file asks for it.

    Args:
        config: The configuration loaded from the ``kili-sdk-config.json`` file.
    """
    if bool(config.get(SIMPLIFY_ERROR_LOGS_CONFIG_KEY, False)):
        _state["enabled_from_config"] = True
        install_error_display_hooks()


def install_error_display_hooks_if_enabled() -> None:
    """Install the display hooks if the simplified error display is enabled."""
    if is_error_simplification_enabled():
        install_error_display_hooks()


def install_error_display_hooks() -> None:
    """Install the hooks rendering SDK errors and warnings as single lines.

    The hooks only alter the display when the simplified error display is
    enabled, and delegate to the previous behavior otherwise. Installing them
    twice is a no-op.
    """
    if sys.excepthook is not _simplified_excepthook:
        _state["previous_excepthook"] = sys.excepthook
        sys.excepthook = _simplified_excepthook

    if warnings.formatwarning is not _simplified_formatwarning:
        _state["previous_formatwarning"] = warnings.formatwarning
        warnings.formatwarning = _simplified_formatwarning

    _install_ipython_hook()


def simplify_graphql_error_message(message: str) -> str:
    """Extract the human-readable part of a backend GraphQL error message.

    Strips the stack-trace lines, the ``[errorCode]`` prefix and the generic
    boilerplate that the backend prepends to the actual cause of the error.
    Messages that do not follow the backend format are returned unchanged.
    """
    simplified = _STACK_FRAME_LINE_REGEX.sub("", message).strip()

    if _CAUSE_SEPARATOR in simplified:
        simplified = simplified.split(_CAUSE_SEPARATOR, 1)[1].strip()
    else:
        simplified = _ERROR_CODE_PREFIX_REGEX.sub("", simplified)

    return simplified or message


def _env_flag_value() -> Optional[bool]:
    raw_value = os.getenv(SIMPLIFY_ERROR_LOGS_ENV_VAR)
    if raw_value is None:
        return None
    return raw_value.strip().lower() in _TRUTHY_ENV_VALUES


def _is_kili_exception_type(exception_type: type) -> bool:
    module_name = getattr(exception_type, "__module__", "") or ""
    return module_name == "kili" or module_name.startswith("kili.")


def _is_kili_file(filename: str) -> bool:
    return f"{os.sep}kili{os.sep}" in filename


def _print_error_line(exception: BaseException) -> None:
    message = str(exception).strip() or exception.__class__.__name__
    stream = sys.stderr
    try:
        is_a_tty = stream.isatty()
    except (AttributeError, ValueError):
        is_a_tty = False
    if is_a_tty:
        message = f"{_RED}{message}{_RESET}"
    stream.write(f"{message}\n")


def _simplified_excepthook(
    exception_type: type[BaseException],
    exception_value: BaseException,
    exception_traceback: Optional[TracebackType],
) -> None:
    if is_error_simplification_enabled() and _is_kili_exception_type(exception_type):
        _print_error_line(exception_value)
        return
    previous_excepthook = _state["previous_excepthook"] or sys.__excepthook__
    previous_excepthook(exception_type, exception_value, exception_traceback)


def _simplified_formatwarning(
    message: Union[Warning, str],
    category: type[Warning],
    filename: str,
    lineno: int,
    line: Optional[str] = None,
) -> str:
    if is_error_simplification_enabled() and _is_kili_file(filename):
        return f"{category.__name__}: {message}\n"
    previous_formatwarning = _state["previous_formatwarning"] or _default_formatwarning
    return previous_formatwarning(message, category, filename, lineno, line)


def _install_ipython_hook() -> None:
    """Register a single-line display of SDK errors in IPython/Jupyter."""
    if "IPython" not in sys.modules:
        # Not running in an IPython/Jupyter shell: sys.excepthook is enough.
        return

    try:
        from IPython.core.getipython import (  # pylint: disable=import-outside-toplevel
            get_ipython,
        )
    except ImportError:
        return

    shell = get_ipython()
    if shell is None:
        return

    def _custom_exception_handler(
        shell_: Any,  # noqa: ANN401
        exception_type: type[BaseException],
        exception_value: BaseException,
        exception_traceback: Optional[TracebackType],
        tb_offset: Optional[int] = None,
    ) -> None:
        if is_error_simplification_enabled() and _is_kili_exception_type(exception_type):
            _print_error_line(exception_value)
            return
        shell_.showtraceback(
            (exception_type, exception_value, exception_traceback), tb_offset=tb_offset
        )

    shell.set_custom_exc((Exception,), _custom_exception_handler)
