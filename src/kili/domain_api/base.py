"""Base class for all domain namespaces in the Kili Python SDK.

This module provides the foundational DomainNamespace class that implements
memory optimization, weak references, and caching for all
domain-specific namespaces.
"""

import weakref
from typing import TYPE_CHECKING, Optional, TypeVar

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy

T = TypeVar("T", bound="DomainNamespace")


class DomainNamespace:
    """Base class for all domain namespaces with performance optimizations.

    This class provides the foundational architecture for domain-based API namespaces
    in the Kili Python SDK, featuring:

    - Memory efficiency through __slots__
    - Weak references to prevent circular references

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
        client: "KiliLegacy",
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
        self._client_ref: "weakref.ReferenceType[KiliLegacy]" = weakref.ref(client)
        self._gateway = gateway
        self._domain_name = domain_name or self.__class__.__name__.lower()

    @property
    def _client(self) -> "KiliLegacy":
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

    def __repr__(self) -> str:
        """Return a string representation of the namespace."""
        try:
            client_info = f"client={self._client.__class__.__name__}"
        except ReferenceError:
            client_info = "client=<garbage collected>"

        return f"{self.__class__.__name__}({client_info}, domain='{self._domain_name}')"
