"""Plugin domain contract using TypedDict.

This module provides a TypedDict-based contract for Plugin entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict

from typeguard import check_type


class PluginContract(TypedDict, total=False):
    """TypedDict contract for Plugin entities.

    This contract represents the core structure of a Plugin as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the plugin
        name: Plugin name
        createdAt: ISO timestamp of creation
        pluginType: Type of plugin (e.g., webhook, function)
        verbose: Whether verbose logging is enabled
        isActivated: Whether the plugin is currently active
    """

    id: str
    name: str
    createdAt: str
    pluginType: str
    verbose: bool
    isActivated: bool


def validate_plugin(data: Dict[str, Any]) -> PluginContract:
    """Validate and return a plugin contract.

    Args:
        data: Dictionary to validate as a PluginContract

    Returns:
        The validated data as a PluginContract

    Raises:
        TypeError: If the data does not match the PluginContract structure
    """
    check_type(data, PluginContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class PluginView:
    """Read-only view wrapper for PluginContract.

    This dataclass provides ergonomic property access to plugin data
    while maintaining the underlying dictionary representation.

    Example:
        >>> plugin_data = {"id": "123", "name": "My Webhook", "isActivated": True, ...}
        >>> view = PluginView(plugin_data)
        >>> print(view.id)
        '123'
        >>> print(view.is_activated)
        True
    """

    __slots__ = ("_data",)

    _data: PluginContract

    @property
    def id(self) -> str:
        """Get plugin ID."""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """Get plugin name."""
        return self._data.get("name", "")

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def plugin_type(self) -> str:
        """Get plugin type."""
        return self._data.get("pluginType", "")

    @property
    def verbose(self) -> bool:
        """Check if verbose logging is enabled."""
        return self._data.get("verbose", False)

    @property
    def is_activated(self) -> bool:
        """Check if plugin is activated."""
        return self._data.get("isActivated", False)

    @property
    def is_active(self) -> bool:
        """Alias for is_activated."""
        return self.is_activated

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the plugin.

        Returns the plugin name.
        """
        return self.name or self.id

    def to_dict(self) -> PluginContract:
        """Get the underlying dictionary representation."""
        return self._data
