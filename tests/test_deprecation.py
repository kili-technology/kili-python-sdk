"""Deprecation tests"""

import inspect

from kili import __version__, client


def test_catch_deprecated_elements_to_remove():
    """Raise an error if a function has a deprecation tag of a version
    that is bigger that the version that is released."""
    functions = inspect.getmembers(client.Kili, inspect.isfunction)
    functions_warning = []
    for function_name, function in functions:
        if hasattr(function, "removed_in"):
            deprecation_version = getattr(function, "removed_in")
            if __version__.split(".")[:2] >= deprecation_version.split("."):
                functions_warning.append(function_name)
    assert len(functions_warning) == 0, (
        f"Functions: {[function_name for function_name in functions_warning]}"
        "are deprecated or have a deprecated argument that should be removed"
        f"in version {__version__}"
    )
