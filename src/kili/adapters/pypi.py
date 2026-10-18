"""PyPI adapter, used to tell a Kili SaaS user when their SDK version is outdated."""

import inspect
import warnings
from typing import Optional
from urllib.parse import urlparse

from kili import __version__
from kili.adapters.http_client import HttpClient

PYPI_JSON_URL = "https://pypi.org/pypi/kili/json"

# Shorter than the 30 seconds the rest of the SDK uses: the client works perfectly well without
# this answer, so a slow PyPI must not hold up every client initialization.
PYPI_TIMEOUT_IN_SECONDS = 3

# Kili SaaS in production, EU and US. On-premise and LTS deployments run the SDK version their
# Kili ships, so they are never asked to upgrade.
SAAS_PRODUCTION_HOSTS = ("cloud.kili-technology.com", "cloud.eastus.kili-technology.com")

# PyPI is asked once per process: a notebook, a script or a plugin run may build several clients.
_latest_versions: dict[str, Optional[str]] = {}


def _parse_version(version: str) -> Optional[tuple[int, ...]]:
    """Parse a release version into a comparable tuple.

    Returns None for anything that is not a plain dotted number, so that development
    installs and pre-releases are never reported as outdated.
    """
    parts = version.split(".")
    if not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def is_saas_production(api_endpoint: str) -> bool:
    """Whether the endpoint is Kili SaaS in production, EU or US."""
    return urlparse(api_endpoint).hostname in SAAS_PRODUCTION_HOSTS


def _fetch_latest_sdk_version(http_client: HttpClient) -> Optional[str]:
    try:
        response = http_client.get(PYPI_JSON_URL, timeout=PYPI_TIMEOUT_IN_SECONDS)
        if response.status_code != 200:  # noqa: PLR2004
            return None
        return response.json()["info"]["version"]
    # Telling the user about an upgrade must never break their script, whatever PyPI answers.
    except Exception:  # noqa: BLE001  # pylint: disable=broad-except  # any failure: no notice
        return None


def get_latest_sdk_version_from_pypi(http_client: HttpClient) -> Optional[str]:
    """Get the latest version of the Kili SDK published on PyPI, pre-releases aside.

    Returns None if the version cannot be retrieved.
    """
    if PYPI_JSON_URL not in _latest_versions:
        _latest_versions[PYPI_JSON_URL] = _fetch_latest_sdk_version(http_client)
    return _latest_versions[PYPI_JSON_URL]


def _stacklevel_of_the_caller_outside_kili() -> int:
    """The `stacklevel` that points the warning of this module's caller at the user's code."""
    level = 1
    frame = inspect.currentframe()
    frame = frame.f_back if frame is not None else None  # the function that warns: stacklevel 1
    while frame is not None and frame.f_globals.get("__name__", "").split(".")[0] == "kili":
        frame = frame.f_back
        level += 1
    return level


def warn_if_sdk_version_is_outdated(http_client: HttpClient, api_endpoint: str) -> None:
    """Warn a Kili SaaS user when a newer version of the Kili SDK is available on PyPI."""
    if not is_saas_production(api_endpoint):
        return

    latest_version = get_latest_sdk_version_from_pypi(http_client)
    if latest_version is None:
        return

    current, latest = _parse_version(__version__), _parse_version(latest_version)
    if current is None or latest is None or current >= latest:
        return

    warnings.warn(
        f"You are using Kili SDK version {__version__}, while version {latest_version} is"
        " available. Upgrade with: pip install --upgrade kili",
        UserWarning,
        stacklevel=_stacklevel_of_the_caller_outside_kili(),
    )
