"""Configuration file loader for the Kili SDK."""

import json
import warnings
from pathlib import Path
from typing import Any, Optional


def load_config_from_file(
    filename: str = "kili-sdk-config.json",
    search_paths: Optional[list[Path]] = None,
) -> dict[str, Any]:
    """Load configuration from a JSON file.

    Searches for the configuration file in the provided search paths.
    If no search paths are provided, searches in the current working directory
    and the user's home directory.

    Args:
        filename: Name of the configuration file. Defaults to "kili-sdk-config.json".
        search_paths: List of directories to search for the configuration file.
            If None, defaults to [cwd, home].

    Returns:
        A dictionary containing the configuration, or an empty dict if no file is found.
    """
    if search_paths is None:
        search_paths = [
            Path.cwd(),
            Path.home(),
        ]

    for search_path in search_paths:
        config_path = search_path / filename
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                warnings.warn(
                    f"Invalid JSON in configuration file '{config_path}': {e}. Skipping this file",
                    UserWarning,
                    stacklevel=2,
                )
                continue
            except OSError as e:
                warnings.warn(
                    f"Could not read configuration file '{config_path}': {e}. Skipping this file.",
                    UserWarning,
                    stacklevel=2,
                )
                continue

    return {}
