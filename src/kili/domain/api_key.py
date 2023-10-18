"""API Key domain."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ApiKeyFilters:
    """Api key filters for running an api key search."""

    api_key_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None
