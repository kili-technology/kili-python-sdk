"""Opt-in simplified display of the SDK errors and warnings.

When error simplification is enabled, an uncaught error raised by the SDK is reported as one
line, the user's line that called the SDK and the message, without traceback. Backend GraphQL
error messages are shown without their technical noise (error codes, stack traces, boilerplate),
and warnings emitted by the SDK are displayed on a single line. Errors raised by the user's own
code keep their full traceback. Only the display changes: an error caught keeps its message.

It can be enabled with the ``KILI_SDK_SIMPLIFY_ERROR_LOGS`` environment variable
(set to ``true``, ``1`` or ``yes``), or with ``"simplify_error_logs": true`` in
the ``kili-sdk-config.json`` configuration file.
"""

import functools
import importlib
import os
import re
import site
import sys
import sysconfig
import traceback
import warnings
from collections.abc import Mapping
from types import FrameType, TracebackType
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

# The installed kili package: a frame of a file under it is the SDK's.
_KILI_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep

_RED = "\033[91m"
_RESET = "\033[0m"

_default_formatwarning = warnings.formatwarning

_state: dict[str, Any] = {
    "enabled_from_config": False,
    "previous_excepthook": None,
    "previous_formatwarning": None,
}

# Exception hooks that format errors the way Python does, rather than a tool of the user's: the
# exceptiongroup backport's (Python 3.10, imported by gql's dependencies) and Ubuntu's crash
# reporter's.
_DEFAULT_EXCEPTHOOK_MODULES = ("exceptiongroup._formatting", "apport_python_hook")


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
    value = config.get(SIMPLIFY_ERROR_LOGS_CONFIG_KEY)
    if value is True:
        _state["enabled_from_config"] = True
    elif value is not None and value is not False:
        warnings.warn(
            f"`{SIMPLIFY_ERROR_LOGS_CONFIG_KEY}` in kili-sdk-config.json is {value!r}: write true or"
            " false. The simplified error display stays off.",
            UserWarning,
            stacklevel=3,
        )
    # also when the environment variable was set after kili was imported
    install_error_display_hooks_if_enabled()


def install_error_display_hooks_if_enabled() -> None:
    """Install the display hooks if the simplified error display is enabled."""
    if is_error_simplification_enabled():
        install_error_display_hooks()


def install_error_display_hooks() -> None:
    """Install the hooks rendering SDK errors and warnings as single lines.

    The hooks only alter the display when the simplified error display is enabled, and delegate
    to the previous behavior otherwise. Installing them twice is a no-op. An exception hook that
    another tool installed (an error tracker, a debugger) is left in place.
    """
    if sys.version_info < (3, 11):
        # Let the exceptiongroup backport patch the traceback module and set its hook first: it
        # skips both when it finds a hook other than Python's, and exception groups then lose their
        # sub-exceptions in every traceback of the process.
        try:
            importlib.import_module("exceptiongroup")  # only installed below Python 3.11
        except ImportError:
            pass

    if _is_default_excepthook(sys.excepthook):
        _state["previous_excepthook"] = sys.excepthook
        sys.excepthook = _simplified_excepthook

    # Once: wrapping a formatter that a later tool wrapped around this one would loop.
    if _state["previous_formatwarning"] is None:
        _state["previous_formatwarning"] = warnings.formatwarning
        warnings.formatwarning = _simplified_formatwarning

    _install_ipython_hook()


def _is_default_excepthook(hook: object) -> bool:
    return hook is sys.__excepthook__ or getattr(hook, "__module__", None) in (
        _DEFAULT_EXCEPTHOOK_MODULES
    )


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
    return os.path.abspath(filename).startswith(_KILI_DIRECTORY)


def _module_name(frame: FrameType) -> str:
    return frame.f_globals.get("__name__", "") or ""


def _is_kili_frame(frame: FrameType) -> bool:
    return _module_name(frame).split(".")[0] == "kili" or _is_kili_file(frame.f_code.co_filename)


@functools.lru_cache(maxsize=1)
def _library_directories() -> tuple[str, ...]:
    paths = sysconfig.get_paths()
    # "scripts" holds the console scripts, the `kili` command's among them
    keys = ("stdlib", "platstdlib", "purelib", "platlib", "scripts")
    directories = [paths[key] for key in keys if key in paths]
    directories += site.getsitepackages() if hasattr(site, "getsitepackages") else []
    directories.append(site.getusersitepackages())
    return tuple(os.path.abspath(directory) + os.sep for directory in directories)


def _is_library_file(filename: str) -> bool:
    return filename.startswith("<frozen") or os.path.abspath(filename).startswith(
        _library_directories()
    )


def _raised_by_kili(
    exception_type: type[BaseException], exception_traceback: Optional[TracebackType]
) -> bool:
    """Whether the error comes from the SDK rather than from the user's own code.

    A kili exception does. Otherwise the code closest to where it was raised decides, the
    libraries the SDK calls (typeguard, requests, the standard library) passed over: an error
    raised in kili's code is the SDK's, one raised in the user's code, a callback the SDK called
    included, is the user's.
    """
    if _is_kili_exception_type(exception_type):
        return True
    for frame, _ in reversed(list(traceback.walk_tb(exception_traceback))):
        if _is_kili_frame(frame):
            return True
        if not _is_library_file(frame.f_code.co_filename):
            return False
    return False


def _user_call_site(exception_traceback: Optional[TracebackType]) -> Optional[str]:
    """The user's line closest to the error, the one that called the SDK, as `file:line`.

    None for the `kili` command, which the user typed rather than wrote.
    """
    call_site = None
    for frame, line_number in traceback.walk_tb(exception_traceback):
        if _module_name(frame).startswith("kili.entrypoints.cli"):
            return None
        if not _is_kili_frame(frame) and not _is_library_file(frame.f_code.co_filename):
            call_site = (frame.f_code.co_filename, line_number)
    if call_site is None:
        return None
    filename, line_number = call_site
    try:
        relative = os.path.relpath(filename) if os.path.isabs(filename) else filename
    except ValueError:  # on Windows, a file on another drive than the working directory
        relative = filename
    shown = filename if relative.startswith("..") else relative
    return f"{shown}:{line_number}"


def _one_line(exception: BaseException, call_site: Optional[str]) -> str:
    name = type(exception).__name__
    # kili's errors that carry a short form of their message: the message itself stays whole
    short_message = getattr(exception, "short_message", None)
    full = short_message if isinstance(short_message, str) and short_message else str(exception)
    message = " ".join(line.strip() for line in full.splitlines() if line.strip())
    if not message:
        message = name
    elif not _is_kili_exception_type(type(exception)):
        message = f"{name}: {message}"  # a ValueError, a KeyError: the type says what went wrong
    return f"{call_site}: {message}" if call_site else message


def _print_error_line(line: str) -> None:
    stream = sys.stderr
    try:
        is_a_tty = stream.isatty()
    except (AttributeError, ValueError):
        is_a_tty = False
    # no-color.org; and a Windows console may not read ANSI colors
    if is_a_tty and not os.getenv("NO_COLOR") and os.name != "nt":
        line = f"{_RED}{line}{_RESET}"
    stream.write(f"{line}\n")


def _simplified_excepthook(
    exception_type: type[BaseException],
    exception_value: BaseException,
    exception_traceback: Optional[TracebackType],
) -> None:
    previous_excepthook = _state["previous_excepthook"] or sys.__excepthook__
    try:
        if is_error_simplification_enabled() and _raised_by_kili(
            exception_type, exception_traceback
        ):
            _print_error_line(_one_line(exception_value, _user_call_site(exception_traceback)))
            return
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught  # never lose the error
        pass
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
        from IPython.core.getipython import (  # pylint: disable=import-outside-toplevel  # optional
            get_ipython,
        )
    except ImportError:
        return

    shell = get_ipython()
    # IPython takes one custom exception handler: one already set is the user's or a tool's.
    if shell is None or shell.custom_exceptions:
        return

    def _custom_exception_handler(
        shell_: Any,  # noqa: ANN401
        exception_type: type[BaseException],
        exception_value: BaseException,
        exception_traceback: Optional[TracebackType],
        tb_offset: Optional[int] = None,
    ) -> None:
        exception_info = (exception_type, exception_value, exception_traceback)
        if is_error_simplification_enabled() and _raised_by_kili(
            exception_type, exception_traceback
        ):
            # what showtraceback does besides printing: %debug and %tb read sys.last_*, %pdb
            shell_._get_exc_info(exception_info)  # pylint: disable=protected-access  # IPython's
            # the line shows right under the cell that raised it
            _print_error_line(_one_line(exception_value, None))
            if shell_.call_pdb:
                shell_.debugger(force=True)
            return
        # as IPython shows an error of the cell's code when no custom handler is set
        shell_.showtraceback(exception_info, tb_offset=tb_offset, running_compiled_code=True)

    shell.set_custom_exc((Exception,), _custom_exception_handler)
