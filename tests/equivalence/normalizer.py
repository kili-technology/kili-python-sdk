"""Payload normalization utilities for equivalence testing.

This module provides utilities to normalize API responses for comparison,
handling differences in structure (dict vs TypedDict) while ensuring
semantic equivalence.
"""

from typing import Any, Dict, List, Set, Union


class PayloadNormalizer:
    """Normalize payloads for semantic equivalence comparison.

    This class handles normalization of API responses to enable comparison
    between legacy dict-based responses and v2 TypedDict-based responses.
    """

    # Fields to ignore during comparison (timestamps may vary slightly, etc.)
    IGNORE_FIELDS: Set[str] = {
        "__typename",  # GraphQL metadata
        "_internal_id",  # Internal tracking fields
    }

    # Fields that should be sorted for consistent comparison
    SORTABLE_LIST_FIELDS: Set[str] = {
        "labels",
        "assets",
        "projects",
        "users",
    }

    @classmethod
    def normalize(
        cls,
        payload: Any,
        sort_lists: bool = True,
        strip_none: bool = False,
    ) -> Any:
        """Normalize a payload for comparison.

        Args:
            payload: The payload to normalize (dict, list, or primitive)
            sort_lists: Whether to sort lists for consistent ordering
            strip_none: Whether to remove None values from dicts

        Returns:
            Normalized payload suitable for comparison
        """
        if payload is None:
            return None

        if isinstance(payload, dict):
            return cls._normalize_dict(payload, sort_lists, strip_none)

        if isinstance(payload, (list, tuple)):
            return cls._normalize_list(list(payload), sort_lists, strip_none)

        # Primitives (str, int, float, bool) are returned as-is
        return payload

    @classmethod
    def _normalize_dict(
        cls,
        data: Dict[str, Any],
        sort_lists: bool,
        strip_none: bool,
    ) -> Dict[str, Any]:
        """Normalize a dictionary."""
        normalized = {}

        for key, value in data.items():
            # Skip ignored fields
            if key in cls.IGNORE_FIELDS:
                continue

            # Skip None values if requested
            if strip_none and value is None:
                continue

            # Recursively normalize nested structures
            normalized[key] = cls.normalize(value, sort_lists, strip_none)

        return normalized

    @classmethod
    def _normalize_list(
        cls,
        data: List[Any],
        sort_lists: bool,
        strip_none: bool,
    ) -> List[Any]:
        """Normalize a list."""
        normalized = [cls.normalize(item, sort_lists, strip_none) for item in data]

        # Sort lists if requested and items are sortable
        if sort_lists and normalized and cls._is_sortable_list(normalized):
            normalized = sorted(normalized, key=cls._sort_key)

        return normalized

    @classmethod
    def _is_sortable_list(cls, items: List[Any]) -> bool:
        """Check if a list can be sorted."""
        if not items:
            return False

        # Lists of dicts with 'id' field can be sorted by id
        if isinstance(items[0], dict) and "id" in items[0]:
            return True

        # Lists of primitives can be sorted
        if isinstance(items[0], (str, int, float, bool)):
            return True

        return False

    @classmethod
    def _sort_key(cls, item: Any) -> Any:
        """Generate a sort key for an item."""
        if isinstance(item, dict):
            # Sort by id if available, otherwise by string representation
            return item.get("id", str(item))
        return item

    @classmethod
    def normalize_for_comparison(
        cls,
        legacy_response: Any,
        v2_response: Any,
    ) -> tuple[Any, Any]:
        """Normalize both legacy and v2 responses for comparison.

        This method applies consistent normalization to both responses,
        handling common differences between legacy and v2 implementations.

        Args:
            legacy_response: Response from legacy implementation
            v2_response: Response from v2 implementation

        Returns:
            Tuple of (normalized_legacy, normalized_v2)
        """
        # Apply standard normalization
        norm_legacy = cls.normalize(legacy_response, sort_lists=True, strip_none=False)
        norm_v2 = cls.normalize(v2_response, sort_lists=True, strip_none=False)

        return norm_legacy, norm_v2


class DiffGenerator:
    """Generate human-readable diffs between payloads."""

    @classmethod
    def generate_diff(
        cls,
        legacy: Any,
        v2: Any,
        path: str = "root",
        max_depth: int = 10,
    ) -> List[str]:
        """Generate a list of differences between two payloads.

        Args:
            legacy: Legacy response
            v2: V2 response
            path: Current path in the data structure
            max_depth: Maximum recursion depth

        Returns:
            List of difference descriptions
        """
        if max_depth <= 0:
            return [f"{path}: Maximum recursion depth reached"]

        diffs: List[str] = []

        # Type mismatch
        if type(legacy) is not type(v2):
            diffs.append(
                f"{path}: Type mismatch - legacy={type(legacy).__name__}, "
                f"v2={type(v2).__name__}"
            )
            return diffs

        # Compare dicts
        if isinstance(legacy, dict):
            diffs.extend(cls._diff_dicts(legacy, v2, path, max_depth))

        # Compare lists
        elif isinstance(legacy, (list, tuple)):
            diffs.extend(cls._diff_lists(legacy, v2, path, max_depth))

        # Compare primitives
        elif legacy != v2:
            diffs.append(f"{path}: Value mismatch - legacy={legacy!r}, v2={v2!r}")

        return diffs

    @classmethod
    def _diff_dicts(
        cls,
        legacy: Dict[str, Any],
        v2: Dict[str, Any],
        path: str,
        max_depth: int,
    ) -> List[str]:
        """Generate diffs for dictionaries."""
        diffs: List[str] = []

        # Keys only in legacy
        legacy_only = set(legacy.keys()) - set(v2.keys())
        if legacy_only:
            diffs.append(f"{path}: Keys only in legacy: {sorted(legacy_only)}")

        # Keys only in v2
        v2_only = set(v2.keys()) - set(legacy.keys())
        if v2_only:
            diffs.append(f"{path}: Keys only in v2: {sorted(v2_only)}")

        # Compare common keys
        common_keys = set(legacy.keys()) & set(v2.keys())
        for key in sorted(common_keys):
            key_path = f"{path}.{key}"
            diffs.extend(cls.generate_diff(legacy[key], v2[key], key_path, max_depth - 1))

        return diffs

    @classmethod
    def _diff_lists(
        cls,
        legacy: Union[List[Any], tuple],
        v2: Union[List[Any], tuple],
        path: str,
        max_depth: int,
    ) -> List[str]:
        """Generate diffs for lists."""
        diffs: List[str] = []

        # Length mismatch
        if len(legacy) != len(v2):
            diffs.append(f"{path}: Length mismatch - legacy={len(legacy)}, v2={len(v2)}")
            # Still compare up to the shorter length
            min_len = min(len(legacy), len(v2))
        else:
            min_len = len(legacy)

        # Compare elements
        for i in range(min_len):
            item_path = f"{path}[{i}]"
            diffs.extend(cls.generate_diff(legacy[i], v2[i], item_path, max_depth - 1))

        return diffs
