import json
from pathlib import Path
from typing import Any, Optional


def load_config_from_file(
    filename: str = "sdk-config.json",
    search_paths: Optional[list[Path]] = None,
) -> dict[str, Any]:
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
            except (json.JSONDecodeError, OSError):
                continue

    return {}
