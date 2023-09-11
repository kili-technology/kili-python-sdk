"""Deprecation tests."""

import inspect

from kili import __version__, client


def test_catch_deprecated_elements_to_remove():
    """Raise an error if a function has been deprecated but not removed."""
    functions = inspect.getmembers(client.Kili, inspect.isfunction)
    functions_warning = []
    for function_name, function in functions:
        if hasattr(function, "removed_in"):
            deprecation_version = function.removed_in  # pyright:ignore[reportGeneralTypeIssues]
            if __version__.split(".")[:2] >= deprecation_version.split("."):
                functions_warning.append(function_name)
    assert len(functions_warning) == 0, (
        f"Functions: {functions_warning}"
        "are deprecated or have a deprecated argument that should be removed"
        f"in version {__version__}"
    )
