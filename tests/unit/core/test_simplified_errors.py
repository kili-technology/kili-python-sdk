"""Tests for the opt-in simplified error display."""

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
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
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


def test_given_the_flag_disabled_when_raising_a_graphql_error_then_the_message_is_legacy():
    error = GraphQLError(error=[{"message": BACKEND_MESSAGE_WITH_STACK}])

    assert str(error).startswith('GraphQL error: "')
    assert "    at " in str(error)


def test_given_the_flag_enabled_when_raising_a_graphql_error_then_the_message_is_short(monkeypatch):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")

    error = GraphQLError(error=[{"message": BACKEND_MESSAGE_WITH_STACK}])

    assert str(error) == SIMPLIFIED_MESSAGE


def test_given_the_flag_enabled_when_raising_a_batched_graphql_error_then_the_index_is_kept(
    monkeypatch,
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")

    error = GraphQLError(error=[{"message": BACKEND_MESSAGE}], batch_number=3)

    assert str(error) == f"{SIMPLIFIED_MESSAGE} (at index 300)"


def test_given_the_flag_enabled_when_the_api_key_is_invalid_then_the_message_is_short(monkeypatch):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")

    error = AuthenticationFailed(
        api_key="rggerg",
        api_endpoint="http://localhost:4001/api/label/v2/graphql",
        error_msg="Api key does not seem to be valid.",
    )

    assert str(error) == "Invalid API key `**gerg`"


def test_given_the_flag_enabled_when_the_api_key_is_missing_then_the_message_is_one_line(
    monkeypatch,
):
    monkeypatch.setenv(SIMPLIFY_ERROR_LOGS_ENV_VAR, "true")

    error = AuthenticationFailed(api_key=None, api_endpoint="https://cloud.kili-technology.com")

    assert "KILI_API_KEY" in str(error)
    assert "\n" not in str(error)


def test_given_the_flag_disabled_when_authentication_fails_then_the_message_is_legacy():
    error = AuthenticationFailed(
        api_key="rggerg",
        api_endpoint="http://localhost:4001/api/label/v2/graphql",
        error_msg="Api key does not seem to be valid.",
    )

    assert "Check your connection and API key." in str(error)
    assert "**gerg" in str(error)


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
        os.sep.join(["", "site-packages", "kili", "client_domain.py"]),
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
