"""Tests for the opt-in simplified error display."""

import io
import os
import sys
import warnings

import pytest

from kili.core import simplified_errors
from kili.core.simplified_errors import (
    SIMPLIFY_ERROR_LOGS_ENV_VAR,
    enable_error_simplification_from_config,
    install_error_display_hooks,
    is_error_simplification_enabled,
    simplify_graphql_error_message,
)
from kili.exceptions import AuthenticationFailed, GraphQLError

BACKEND_MESSAGE = (
    "[notFound] Resource not found. -- This can be due to:"
    " Project with id cme2rmsjdg0k4an0w4j0iggq3 not found"
)

BACKEND_MESSAGE_WITH_STACK = (
    BACKEND_MESSAGE
    + "\n    at <anonymous> (/app/src/context/localContext/projectContext/index.ts:388:9)"
    + "\n    at Array.map (<anonymous>)"
    + "\n    at process.processTicksAndRejections (node:internal/process/task_queues:103:5)"
)

SIMPLIFIED_MESSAGE = "Project with id cme2rmsjdg0k4an0w4j0iggq3 not found"


@pytest.fixture(autouse=True)
def _reset_simplified_errors_state(monkeypatch):
    """Isolate each test from the environment and restore the display hooks."""
    monkeypatch.delenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, raising=False)
    monkeypatch.setitem(simplified_errors._state, "enabled_from_config", False)
    monkeypatch.setitem(simplified_errors._state, "previous_excepthook", None)
    monkeypatch.setitem(simplified_errors._state, "previous_formatwarning", None)
    monkeypatch.setattr(sys, "excepthook", sys.__excepthook__)
    monkeypatch.setattr(warnings, "formatwarning", warnings.formatwarning)


def test_given_no_configuration_when_checking_the_flag_then_it_is_disabled():
    assert is_error_simplification_enabled() is False


@pytest.mark.parametrize("value", ["true", "True", "1", "yes"])
def test_given_a_truthy_env_value_when_checking_the_flag_then_it_is_enabled(monkeypatch, value):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, value)

    assert is_error_simplification_enabled() is True


@pytest.mark.parametrize("value", ["false", "0", "no", ""])
def test_given_a_falsy_env_value_when_checking_the_flag_then_it_is_disabled(monkeypatch, value):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, value)

    assert is_error_simplification_enabled() is False


def test_given_a_config_file_enabling_it_when_checking_the_flag_then_it_is_enabled():
    enable_error_simplification_from_config({"simplify_error_logs": True})

    assert is_error_simplification_enabled() is True


def test_given_a_falsy_env_value_when_the_config_file_enables_it_then_the_env_wins(monkeypatch):
    enable_error_simplification_from_config({"simplify_error_logs": True})
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "false")

    assert is_error_simplification_enabled() is False


def test_given_a_backend_message_when_simplifying_then_only_the_cause_remains():
    assert simplify_graphql_error_message(BACKEND_MESSAGE) == SIMPLIFIED_MESSAGE


def test_given_a_message_with_stack_traces_when_simplifying_then_they_are_stripped():
    assert simplify_graphql_error_message(BACKEND_MESSAGE_WITH_STACK) == SIMPLIFIED_MESSAGE


def test_given_a_message_without_cause_when_simplifying_then_the_code_prefix_is_stripped():
    message = "[accessDenied] Access denied. Verify your credentials."

    assert simplify_graphql_error_message(message) == "Access denied. Verify your credentials."


def test_given_a_plain_message_when_simplifying_then_it_is_unchanged():
    assert (
        simplify_graphql_error_message("GraphQL response contains no data")
        == "GraphQL response contains no data"
    )


def test_given_a_graphql_error_then_its_message_stays_whole_and_its_short_form_is_kept_beside():
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE_WITH_STACK}])

    assert str(error) == f'GraphQL error: "{BACKEND_MESSAGE_WITH_STACK}"'
    assert error.short_message == SIMPLIFIED_MESSAGE


@pytest.mark.parametrize("flag", ["true", "false"])
def test_given_the_flag_either_way_when_raising_a_graphql_error_then_its_message_is_the_same(
    monkeypatch, flag
):
    # kili's own code reads str(error) (storages, users): a display setting must not change it
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, flag)

    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}])

    assert str(error) == f'GraphQL error: "{BACKEND_MESSAGE}"'


def test_given_a_batched_graphql_error_then_its_short_form_keeps_the_index():
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}], batch_number=3)

    assert error.short_message == f"{SIMPLIFIED_MESSAGE} (at index 300)"
    assert str(error) == f'GraphQL error at index 300: "{BACKEND_MESSAGE}"'


@pytest.mark.parametrize(
    ("error_msg", "expected"),
    [
        (
            "Api key does not seem to be valid.",
            "API key `**gerg` refused by http://localhost:4001/api/label/v2/graphql: check the key"
            " and the endpoint.",
        ),
        (
            "Connection refused",
            "API key `**gerg` refused by http://localhost:4001/api/label/v2/graphql: Connection"
            " refused",
        ),
    ],
)
def test_given_a_refused_api_key_then_the_short_form_names_the_endpoint(error_msg, expected):
    error = AuthenticationFailed(
        api_key="rggerg",
        api_endpoint="http://localhost:4001/api/label/v2/graphql",
        error_msg=error_msg,
    )

    assert error.short_message == expected
    assert "Check your connection and API key." in str(error)


def test_given_no_api_key_then_the_short_form_is_one_line():
    error = AuthenticationFailed(api_key=None, api_endpoint="https://cloud.kili-technology.com")

    assert "KILI_API_KEY" in error.short_message
    assert "\n" not in error.short_message


def test_given_the_flag_enabled_when_a_kili_error_is_uncaught_then_a_single_line_is_printed(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}])
    sys.excepthook(type(error), error, None)

    assert capsys.readouterr().err == f"{SIMPLIFIED_MESSAGE}\n"


def test_given_the_flag_enabled_when_a_non_kili_error_is_uncaught_then_the_traceback_is_kept(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    try:
        raise ValueError("boom")
    except ValueError:
        exception_info = sys.exc_info()
    sys.excepthook(*exception_info)

    assert "Traceback" in capsys.readouterr().err


def test_given_the_flag_disabled_when_a_kili_error_is_uncaught_then_the_traceback_is_kept(capsys):
    install_error_display_hooks()

    try:
        raise GraphQLError(error=[{"message": BACKEND_MESSAGE}])
    except GraphQLError:
        exception_info = sys.exc_info()
    sys.excepthook(*exception_info)

    assert "Traceback" in capsys.readouterr().err


def test_given_the_flag_enabled_when_a_kili_warning_is_emitted_then_it_is_one_line(monkeypatch):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    formatted = warnings.formatwarning(
        "Client domain api is still a work in progress.",
        UserWarning,
        os.path.join(simplified_errors._KILI_DIRECTORY, "client_domain.py"),
        100,
    )

    assert formatted == "UserWarning: Client domain api is still a work in progress.\n"


def test_given_the_flag_enabled_when_a_non_kili_warning_is_emitted_then_the_format_is_default(
    monkeypatch,
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    filename = os.sep.join(["", "site-packages", "other", "module.py"])
    formatted = warnings.formatwarning("Some warning.", UserWarning, filename, 42)

    assert filename in formatted
    assert "42" in formatted


def test_given_installed_hooks_when_installing_again_then_it_is_a_no_op():
    install_error_display_hooks()
    first_excepthook = sys.excepthook
    first_formatwarning = warnings.formatwarning

    install_error_display_hooks()

    assert sys.excepthook is first_excepthook
    assert warnings.formatwarning is first_formatwarning


def _in_kili(source: str) -> dict:
    """Functions compiled as if they were the SDK's: their frames are in the kili package."""
    namespace: dict = {}
    filename = os.path.join(simplified_errors._KILI_DIRECTORY, "_fake_sdk_module.py")
    exec(compile(source, filename, "exec"), namespace)  # pylint: disable=exec-used  # test code
    return namespace


def _uncaught(function, *args) -> tuple:
    try:
        function(*args)
    except Exception:  # pylint: disable=broad-exception-caught  # whatever the case raises
        return sys.exc_info()
    raise AssertionError("nothing raised")


def test_given_the_flag_enabled_when_the_sdk_raises_a_builtin_error_then_one_line_names_it(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    sdk = _in_kili("def fail():\n    raise ValueError('No user has the email a@b.c')\n")

    exception_info = _uncaught(sdk["fail"])
    sys.excepthook(*exception_info)

    line = exception_info[2].tb_lineno
    err = capsys.readouterr().err
    assert err == f"{os.path.relpath(__file__)}:{line}: ValueError: No user has the email a@b.c\n"


def test_given_the_flag_enabled_when_a_library_the_sdk_calls_raises_then_one_line_is_printed(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    sdk = _in_kili("import json\ndef parse():\n    return json.loads('{')\n")

    sys.excepthook(*_uncaught(sdk["parse"]))

    err = capsys.readouterr().err
    assert "Traceback" not in err
    assert err.count("\n") == 1
    assert ": JSONDecodeError: Expecting property name" in err


def test_given_the_flag_enabled_when_a_callback_the_sdk_calls_raises_then_the_traceback_is_kept(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    sdk = _in_kili("def call(callback):\n    return callback()\n")

    def users_callback():
        raise KeyError("my_bug")

    sys.excepthook(*_uncaught(sdk["call"], users_callback))

    err = capsys.readouterr().err
    assert "Traceback" in err
    assert "users_callback" in err


def test_given_the_flag_enabled_when_a_kili_error_is_raised_through_the_sdk_then_the_call_site_leads(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    sdk = _in_kili(
        "from kili.exceptions import GraphQLError\n"
        "def query(message):\n"
        "    raise GraphQLError(error=[{'message': message}])\n"
    )

    exception_info = _uncaught(sdk["query"], BACKEND_MESSAGE_WITH_STACK)
    sys.excepthook(*exception_info)

    line = exception_info[2].tb_lineno
    assert capsys.readouterr().err == f"{os.path.relpath(__file__)}:{line}: {SIMPLIFIED_MESSAGE}\n"


def test_given_a_user_file_under_a_folder_named_kili_then_it_is_not_the_sdk_s():
    assert not simplified_errors._is_kili_file(os.sep.join(["", "home", "me", "kili", "script.py"]))
    assert simplified_errors._is_kili_file(
        os.path.join(simplified_errors._KILI_DIRECTORY, "client.py")
    )


def test_given_an_exception_hook_set_by_another_tool_when_installing_then_it_is_kept(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    received = []
    monkeypatch.setattr(sys, "excepthook", lambda *exception_info: received.append(exception_info))

    install_error_display_hooks()
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}])
    sys.excepthook(type(error), error, None)

    assert len(received) == 1
    assert capsys.readouterr().err == ""


def test_given_the_exceptiongroup_backport_hook_when_installing_then_it_is_replaced_and_delegated_to(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    received = []

    def exceptiongroup_excepthook(*exception_info):
        received.append(exception_info)

    exceptiongroup_excepthook.__module__ = "exceptiongroup._formatting"
    monkeypatch.setattr(sys, "excepthook", exceptiongroup_excepthook)

    install_error_display_hooks()
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}])
    sys.excepthook(type(error), error, None)
    sys.excepthook(*_uncaught(lambda: {}["user's own key"]))

    assert capsys.readouterr().err == f"{SIMPLIFIED_MESSAGE}\n"
    assert len(received) == 1  # the user's KeyError, formatted by the hook kili replaced


def test_given_a_call_site_on_another_drive_when_printing_then_its_full_path_is_shown(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    sdk = _in_kili("def fail():\n    raise ValueError('bad input')\n")
    exception_info = _uncaught(sdk["fail"])

    def relpath_across_drives(path, start=None):
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr(os.path, "relpath", relpath_across_drives)
    sys.excepthook(*exception_info)

    assert capsys.readouterr().err.startswith(f"{__file__}:")


def test_given_the_variable_set_after_kili_was_imported_when_a_client_starts_then_hooks_install(
    monkeypatch,
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")  # e.g. load_dotenv() after the imports

    enable_error_simplification_from_config({})  # what each client does when it starts

    assert sys.excepthook is simplified_errors._simplified_excepthook


@pytest.mark.parametrize("value", ["true", 1, "yes"])
def test_given_a_config_value_that_is_no_boolean_then_it_warns_and_stays_off(value):
    with pytest.warns(UserWarning, match="write true or false"):
        enable_error_simplification_from_config({"simplify_error_logs": value})

    assert is_error_simplification_enabled() is False


def test_given_a_tool_wrapping_the_warning_formatter_when_installing_again_then_it_does_not_loop(
    monkeypatch,
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    kili_formatter = warnings.formatwarning
    monkeypatch.setattr(warnings, "formatwarning", lambda *args: "tool: " + kili_formatter(*args))

    install_error_display_hooks()  # a second client

    assert warnings.formatwarning("Some warning.", UserWarning, "script.py", 3).startswith("tool: ")


def test_given_the_kili_command_when_it_fails_then_the_line_has_no_location(monkeypatch, capsys):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    namespace: dict = {"__name__": "kili.entrypoints.cli._fake_command"}
    exec(  # pylint: disable=exec-used  # test code
        compile(
            "from kili.exceptions import GraphQLError\n"
            "def main(message):\n"
            "    raise GraphQLError(error=[{'message': message}])\n",
            os.path.join(simplified_errors._KILI_DIRECTORY, "entrypoints", "_fake_command.py"),
            "exec",
        ),
        namespace,
    )

    sys.excepthook(*_uncaught(namespace["main"], BACKEND_MESSAGE))

    assert capsys.readouterr().err == f"{SIMPLIFIED_MESSAGE}\n"


class _Terminal(io.StringIO):
    def isatty(self) -> bool:
        return True


@pytest.mark.parametrize(("no_color", "colored"), [(None, True), ("1", False)])
def test_given_a_terminal_when_printing_then_the_line_is_red_unless_no_color(
    monkeypatch, no_color, colored
):
    terminal = _Terminal()
    monkeypatch.setattr(sys, "stderr", terminal)
    monkeypatch.setattr(os, "name", "posix")
    if no_color is None:
        monkeypatch.delenv("NO_COLOR", raising=False)
    else:
        monkeypatch.setenv("NO_COLOR", no_color)

    simplified_errors._print_error_line("Project not found")

    assert ("\033[91m" in terminal.getvalue()) is colored


def test_given_the_hook_failing_when_an_error_is_uncaught_then_the_previous_hook_shows_it(
    monkeypatch, capsys
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    def broken(*args):
        raise RuntimeError("bug in the display")

    monkeypatch.setattr(simplified_errors, "_one_line", broken)
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}])
    sys.excepthook(type(error), error, None)

    assert "GraphQLError" in capsys.readouterr().err


@pytest.fixture()
def ipython_shell(monkeypatch):
    interactiveshell = pytest.importorskip("IPython.core.interactiveshell")
    shell = interactiveshell.InteractiveShell.instance()
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: shell)
    shell.set_custom_exc((), None)
    yield shell
    shell.set_custom_exc((), None)
    interactiveshell.InteractiveShell.clear_instance()


def test_given_ipython_when_a_kili_error_is_raised_then_one_line_and_the_debugger_s_state(
    monkeypatch, capsys, ipython_shell
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    ipython_shell.user_ns["sdk"] = _in_kili(
        "from kili.exceptions import GraphQLError\n"
        "def query(message):\n"
        "    raise GraphQLError(error=[{'message': message}])\n"
    )
    ipython_shell.user_ns["message"] = BACKEND_MESSAGE

    result = ipython_shell.run_cell("sdk['query'](message)")

    assert capsys.readouterr().err == f"{SIMPLIFIED_MESSAGE}\n"
    assert isinstance(result.error_in_exec, GraphQLError)  # the cell failed: Run All stops
    assert sys.last_value is result.error_in_exec  # what %debug and %tb read


def test_given_ipython_when_the_user_s_code_fails_then_ipython_shows_its_traceback(
    monkeypatch, capsys, ipython_shell
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()

    ipython_shell.run_cell("{}['my own key']")

    captured = capsys.readouterr()
    assert "KeyError" in captured.out + captured.err
    assert "Traceback" in captured.out + captured.err


def test_given_ipython_with_pdb_on_when_a_kili_error_is_raised_then_the_debugger_starts(
    monkeypatch, ipython_shell
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")
    install_error_display_hooks()
    started = []
    monkeypatch.setattr(ipython_shell, "debugger", lambda force=False: started.append(force))
    ipython_shell.call_pdb = True
    ipython_shell.user_ns["sdk"] = _in_kili("def fail():\n    raise ValueError('bad input')\n")

    ipython_shell.run_cell("sdk['fail']()")

    assert started == [True]
