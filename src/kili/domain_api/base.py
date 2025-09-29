"""Base class for all domain namespaces in the Kili Python SDK.

This module provides the foundational DomainNamespace class that implements
memory optimization, weak references, and caching for all
domain-specific namespaces.
"""

import weakref
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway

if TYPE_CHECKING:
    from kili.client import Kili

T = TypeVar("T", bound="DomainNamespace")


class DomainNamespace:
    """Base class for all domain namespaces with performance optimizations.

    This class provides the foundational architecture for domain-based API namespaces
    in the Kili Python SDK, featuring:

    - Memory efficiency through __slots__
    - Weak references to prevent circular references
    - LRU caching for frequently accessed operations

    All domain namespaces (assets, labels, projects, etc.) should inherit from this class.
    """

    __slots__ = (
        "_client_ref",
        "_gateway",
        "_domain_name",
        "__weakref__",
    )

    def __init__(
        self,
        client: "Kili",
        gateway: KiliAPIGateway,
        domain_name: Optional[str] = None,
    ) -> None:
        """Initialize the domain namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
            domain_name: Optional domain name for debugging/logging purposes
        """
        # Use weak reference to prevent circular references between client and namespaces
        self._client_ref: "weakref.ReferenceType[Kili]" = weakref.ref(client)
        self._gateway = gateway
        self._domain_name = domain_name or self.__class__.__name__.lower()

    @property
    def client(self) -> "Kili":
        """Get the Kili client instance.

        Returns:
            The Kili client instance

        Raises:
            ReferenceError: If the client instance has been garbage collected
        """
        client = self._client_ref()
        if client is None:
            raise ReferenceError(
                f"The Kili client instance for {self._domain_name} namespace "
                "has been garbage collected"
            )
        return client

    @property
    def gateway(self) -> KiliAPIGateway:
        """Get the KiliAPIGateway instance for API operations.

        Returns:
            The KiliAPIGateway instance
        """
        return self._gateway

    @property
    def domain_name(self) -> str:
        """Get the domain name for this namespace.

        Returns:
            The domain name string
        """
        return self._domain_name

    def refresh(self) -> None:
        """Refresh the gateway connection and clear any cached data.

        This method should be called to synchronize with the gateway state
        and ensure fresh data is retrieved on subsequent operations.
        """
        # Clear LRU caches for this instance
        self._clear_lru_caches()

        # Subclasses can override this to perform additional refresh operations
        self._refresh_implementation()

    def _clear_lru_caches(self) -> None:
        """Clear all LRU caches for this instance."""
        # Find and clear all lru_cache decorated methods
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "cache_clear"):
                attr.cache_clear()

    def _refresh_implementation(self) -> None:
        """Override this method in subclasses for domain-specific refresh logic."""

    @lru_cache(maxsize=128)
    def _cached_gateway_operation(self, operation_name: str, cache_key: str) -> Any:
        """Perform a cached gateway operation.

        This is a template method that subclasses can use for caching
        frequently accessed gateway operations.

        Args:
            operation_name: Name of the gateway operation
            cache_key: Unique key for caching this operation

        Returns:
            The result of the gateway operation
        """
        # This is a placeholder - subclasses should override with specific logic
        # pylint: disable=unused-argument
        return None

    def __repr__(self) -> str:
        """Return a string representation of the namespace."""
        try:
            client_info = f"client={self.client.__class__.__name__}"
        except ReferenceError:
            client_info = "client=<garbage collected>"

        return f"{self.__class__.__name__}({client_info}, domain='{self.domain_name}')"
