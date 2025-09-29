"""Cloud Storage domain namespace for the Kili Python SDK."""

from kili.domain_api.base import DomainNamespace


class CloudStorageNamespace(DomainNamespace):
    """Cloud Storage domain namespace providing cloud storage operations.

    This namespace provides access to all cloud storage functionality
    including managing integrations and storage configurations.
    """

    def __init__(self, client, gateway):
        """Initialize the cloud storage namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "cloud_storage")

    # Cloud storage operations will be implemented here
    # For now, this serves as a placeholder for the lazy loading implementation
