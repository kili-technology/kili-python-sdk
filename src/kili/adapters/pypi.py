"""PyPI adapter, used to tell the user when their SDK version is outdated."""

import warnings
from typing import Optional

from kili import __version__
from kili.adapters.http_client import HttpClient

PYPI_JSON_URL = "https://pypi.org/pypi/kili/json"

# Shorter than the 30 seconds the rest of the SDK uses: the client works perfectly well without
# this answer, so a slow PyPI must not hold up every client initialization.
PYPI_TIMEOUT_IN_SECONDS = 3


def _parse_version(version: str) -> Optional[tuple[int, ...]]:
    """Parse a release version into a comparable tuple.

    Returns None for anything that is not a plain dotted number, so that development
    installs and pre-releases are never reported as outdated.
    """
    parts = version.split(".")
    if not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def get_latest_sdk_version_from_pypi(http_client: HttpClient) -> Optional[str]:
    """Get the latest version of the Kili SDK published on PyPI.

    Returns None if the version cannot be retrieved.
    """
    try:
        response = http_client.get(PYPI_JSON_URL, timeout=PYPI_TIMEOUT_IN_SECONDS)
        if response.status_code != 200:  # noqa: PLR2004
            return None
        return response.json()["info"]["version"]
    except Exception:  # noqa: BLE001  # pylint: disable=broad-except
        # Telling the user about an upgrade must never break their script, whatever PyPI answers.
        return None


def warn_if_sdk_version_is_outdated(http_client: HttpClient) -> None:
    """Warn the user when a newer version of the Kili SDK is available on PyPI."""
    latest_version = get_latest_sdk_version_from_pypi(http_client)
    if latest_version is None:
        return

    current, latest = _parse_version(__version__), _parse_version(latest_version)
    if current is None or latest is None or current >= latest:
        return

    message = f"""
                You are using Kili SDK version {__version__}, while version {latest_version} is available.
                You should upgrade with: pip install --upgrade kili."""
    warnings.warn(message, UserWarning, stacklevel=2)
