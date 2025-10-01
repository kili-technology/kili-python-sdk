"""Integrations domain namespace for the Kili Python SDK."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.domain.cloud_storage import DataIntegrationPlatform, DataIntegrationStatus
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.presentation.client.cloud_storage import CloudStorageClientMethods


class IntegrationsNamespace(DomainNamespace):
    """Integrations domain namespace providing cloud storage integration operations.

    This namespace provides access to all cloud storage integration functionality
    including listing, creating, updating, and deleting integrations with external
    cloud storage providers (AWS, Azure, GCP, Custom S3).

    Cloud storage integrations represent configured connections to external storage
    services that can be connected to projects via connections. Each integration
    contains credentials and configuration for accessing a specific cloud storage
    service.

    The namespace provides the following main operations:
    - list(): Query and list cloud storage integrations
    - count(): Count integrations matching specified criteria
    - create(): Create a new cloud storage integration
    - update(): Update an existing integration's configuration
    - delete(): Remove a cloud storage integration

    Examples:
        >>> kili = Kili()
        >>> # List all integrations in your organization
        >>> integrations = kili.integrations.list()

        >>> # Create a new AWS S3 integration
        >>> result = kili.integrations.create(
        ...     platform="AWS",
        ...     name="My Production S3 Bucket",
        ...     s3_bucket_name="my-production-bucket",
        ...     s3_region="us-east-1",
        ...     s3_access_key="AKIAIOSFODNN7EXAMPLE",
        ...     s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        ... )

        >>> # Update integration configuration
        >>> result = kili.integrations.update(
        ...     integration_id="integration_123",
        ...     name="Updated Integration Name",
        ...     allowed_paths=["/data/training", "/data/validation"]
        ... )

        >>> # Count integrations by platform
        >>> aws_count = kili.integrations.count(platform="AWS")

        >>> # Delete an integration
        >>> result = kili.integrations.delete("integration_123")
    """

    def __init__(self, client, gateway):
        """Initialize the integrations namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "integrations")

    @overload
    def list(
        self,
        integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def list(
        self,
        integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def list(
        self,
        integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        """Get a generator or a list of cloud storage integrations that match a set of criteria.

        This method provides a simplified interface for querying cloud storage integrations,
        making it easier to discover and manage external service integrations configured
        in your organization.

        Args:
            integration_id: ID of a specific cloud storage integration to retrieve.
            name: Name filter for the cloud storage integration.
            platform: Platform filter for the cloud storage integration.
                Available platforms: "AWS", "Azure", "GCP", "CustomS3".
            status: Status filter for the cloud storage integration.
                Available statuses: "CONNECTED", "DISCONNECTED", "CHECKING".
            organization_id: ID of the organization to filter integrations by.
            fields: All the fields to request among the possible fields for the integrations.
                Available fields include:
                - id: Integration identifier
                - name: Integration name
                - platform: Platform type (AWS, Azure, GCP, CustomS3)
                - status: Connection status (CONNECTED, DISCONNECTED, CHECKING)
                - allowedPaths: List of allowed storage paths
                See the documentation for all possible fields.
            first: Maximum number of integrations to return.
            skip: Number of integrations to skip (ordered by creation date).
            disable_tqdm: If True, the progress bar will be disabled.
            as_generator: If True, a generator on the integrations is returned.

        Returns:
            An iterable of cloud storage integrations matching the criteria.

        Examples:
            >>> # List all integrations
            >>> integrations = kili.integrations.list(as_generator=False)

            >>> # Get a specific integration
            >>> integration = kili.integrations.list(
            ...     integration_id="integration_123",
            ...     as_generator=False
            ... )

            >>> # List AWS integrations only
            >>> aws_integrations = kili.integrations.list(
            ...     platform="AWS",
            ...     as_generator=False
            ... )

            >>> # List integrations with custom fields
            >>> integrations = kili.integrations.list(
            ...     fields=["id", "name", "platform", "allowedPaths"],
            ...     as_generator=False
            ... )

            >>> # List integrations with pagination
            >>> first_page = kili.integrations.list(
            ...     first=10,
            ...     skip=0,
            ...     as_generator=False
            ... )
        """
        # Access the legacy method directly by calling it from the mixin class
        return CloudStorageClientMethods.cloud_storage_integrations(
            self.client,
            cloud_storage_integration_id=integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

    @typechecked
    def count(
        self,
        integration_id: Optional[str] = None,
        name: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        organization_id: Optional[str] = None,
    ) -> int:
        """Count and return the number of cloud storage integrations that match a set of criteria.

        This method provides a convenient way to count integrations without retrieving
        the full data, useful for pagination and analytics.

        Args:
            integration_id: ID of a specific cloud storage integration to count.
            name: Name filter for the cloud storage integration.
            platform: Platform filter for the cloud storage integration.
                Available platforms: "AWS", "Azure", "GCP", "CustomS3".
            status: Status filter for the cloud storage integration.
                Available statuses: "CONNECTED", "DISCONNECTED", "CHECKING".
            organization_id: ID of the organization to filter integrations by.

        Returns:
            The number of cloud storage integrations that match the criteria.

        Examples:
            >>> # Count all integrations
            >>> total = kili.integrations.count()

            >>> # Count AWS integrations
            >>> aws_count = kili.integrations.count(platform="AWS")

            >>> # Count connected integrations
            >>> connected_count = kili.integrations.count(status="CONNECTED")

            >>> # Count integrations by name pattern
            >>> prod_count = kili.integrations.count(name="Production*")
        """
        # Access the legacy method directly by calling it from the mixin class
        return CloudStorageClientMethods.count_cloud_storage_integrations(
            self.client,
            cloud_storage_integration_id=integration_id,
            name=name,
            platform=platform,
            status=status,
            organization_id=organization_id,
        )

    @typechecked
    def create(
        self,
        platform: DataIntegrationPlatform,
        name: str,
        fields: ListOrTuple[str] = (
            "id",
            "name",
            "status",
            "platform",
            "allowedPaths",
        ),
        allowed_paths: Optional[List[str]] = None,
        allowed_projects: Optional[List[str]] = None,
        aws_access_point_arn: Optional[str] = None,
        aws_role_arn: Optional[str] = None,
        aws_role_external_id: Optional[str] = None,
        azure_connection_url: Optional[str] = None,
        azure_is_using_service_credentials: Optional[bool] = None,
        azure_sas_token: Optional[str] = None,
        azure_tenant_id: Optional[str] = None,
        gcp_bucket_name: Optional[str] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
        s3_access_key: Optional[str] = None,
        s3_bucket_name: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
        s3_region: Optional[str] = None,
        s3_secret_key: Optional[str] = None,
        s3_session_token: Optional[str] = None,
    ) -> Dict:
        """Create a new cloud storage integration.

        This method creates a new integration with external cloud storage providers,
        enabling your organization to connect projects to cloud storage services.
        Different platforms require different sets of parameters for authentication
        and configuration.

        Args:
            platform: Platform of the cloud storage integration.
                Must be one of: "AWS", "Azure", "GCP", "CustomS3".
            name: Name of the cloud storage integration.
            fields: All the fields to request among the possible fields for the integration.
                Available fields include: id, name, status, platform, allowedPaths, etc.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_projects: List of project IDs allowed to use this integration.
            aws_access_point_arn: AWS access point ARN for VPC endpoint access.
            aws_role_arn: AWS IAM role ARN for cross-account access.
            aws_role_external_id: AWS role external ID for additional security.
            azure_connection_url: Azure Storage connection URL.
            azure_is_using_service_credentials: Whether Azure uses service credentials.
            azure_sas_token: Azure Shared Access Signature token.
            azure_tenant_id: Azure tenant ID for multi-tenant applications.
            gcp_bucket_name: Google Cloud Storage bucket name.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.
            s3_access_key: S3-compatible access key for authentication.
            s3_bucket_name: S3 bucket name for AWS or S3-compatible storage.
            s3_endpoint: S3 endpoint URL for custom S3-compatible services.
            s3_region: S3 region for AWS S3 buckets.
            s3_secret_key: S3-compatible secret key for authentication.
            s3_session_token: S3 session token for temporary credentials.

        Returns:
            A dictionary containing the created integration information.

        Raises:
            ValueError: If required parameters for the specified platform are missing.
            RuntimeError: If the integration cannot be created due to invalid credentials
                         or configuration errors.
            Exception: If an unexpected error occurs during integration creation.

        Examples:
            >>> # Create AWS S3 integration
            >>> result = kili.integrations.create(
            ...     platform="AWS",
            ...     name="Production S3 Bucket",
            ...     s3_bucket_name="my-production-bucket",
            ...     s3_region="us-east-1",
            ...     s3_access_key="AKIAIOSFODNN7EXAMPLE",
            ...     s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            ... )

            >>> # Create Azure Blob Storage integration
            >>> result = kili.integrations.create(
            ...     platform="Azure",
            ...     name="Azure Production Storage",
            ...     azure_connection_url="https://myaccount.blob.core.windows.net/",
            ...     azure_sas_token="sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=..."
            ... )

            >>> # Create GCP integration
            >>> result = kili.integrations.create(
            ...     platform="GCP",
            ...     name="GCP Production Bucket",
            ...     gcp_bucket_name="my-gcp-bucket"
            ... )

            >>> # Create custom S3 integration with access restrictions
            >>> result = kili.integrations.create(
            ...     platform="CustomS3",
            ...     name="MinIO Development Storage",
            ...     s3_endpoint="http://localhost:9000",
            ...     s3_bucket_name="dev-bucket",
            ...     s3_access_key="minioadmin",
            ...     s3_secret_key="minioadmin",
            ...     allowed_paths=["/datasets", "/models"]
            ... )

            >>> # Access the integration ID
            >>> integration_id = result["id"]
        """
        # Validate input parameters
        if not name or not name.strip():
            raise ValueError("name cannot be empty or None")

        # Platform-specific validation
        if platform == "AWS" and not (s3_bucket_name and s3_region):
            raise ValueError("AWS platform requires s3_bucket_name and s3_region")

        if platform == "Azure" and not azure_connection_url:
            raise ValueError("Azure platform requires azure_connection_url")

        if platform == "GCP" and not gcp_bucket_name:
            raise ValueError("GCP platform requires gcp_bucket_name")

        if platform == "CustomS3" and not (s3_endpoint and s3_bucket_name):
            raise ValueError("CustomS3 platform requires s3_endpoint and s3_bucket_name")

        # Access the legacy method directly by calling it from the mixin class
        try:
            return CloudStorageClientMethods.create_cloud_storage_integration(
                self.client,
                platform=platform,
                name=name,
                fields=fields,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                aws_access_point_arn=aws_access_point_arn,
                aws_role_arn=aws_role_arn,
                aws_role_external_id=aws_role_external_id,
                azure_connection_url=azure_connection_url,
                azure_is_using_service_credentials=azure_is_using_service_credentials,
                azure_sas_token=azure_sas_token,
                azure_tenant_id=azure_tenant_id,
                gcp_bucket_name=gcp_bucket_name,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
                s3_access_key=s3_access_key,
                s3_bucket_name=s3_bucket_name,
                s3_endpoint=s3_endpoint,
                s3_region=s3_region,
                s3_secret_key=s3_secret_key,
                s3_session_token=s3_session_token,
            )
        except Exception as e:
            # Enhanced error handling for creation failures
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create integration '{name}': Invalid credentials for "
                    f"platform '{platform}'. Please verify your authentication parameters. "
                    f"Details: {e!s}"
                ) from e
            if "bucket" in str(e).lower() or "container" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create integration '{name}': Storage container not found "
                    f"or inaccessible for platform '{platform}'. Please verify the "
                    f"bucket/container name and permissions. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create integration '{name}': Insufficient permissions "
                    f"for platform '{platform}'. Please verify your access rights. "
                    f"Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def update(
        self,
        integration_id: str,
        allowed_paths: Optional[List[str]] = None,
        allowed_projects: Optional[List[str]] = None,
        aws_access_point_arn: Optional[str] = None,
        aws_role_arn: Optional[str] = None,
        aws_role_external_id: Optional[str] = None,
        azure_connection_url: Optional[str] = None,
        azure_is_using_service_credentials: Optional[bool] = None,
        azure_sas_token: Optional[str] = None,
        azure_tenant_id: Optional[str] = None,
        gcp_bucket_name: Optional[str] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
        name: Optional[str] = None,
        organization_id: Optional[str] = None,
        platform: Optional[DataIntegrationPlatform] = None,
        status: Optional[DataIntegrationStatus] = None,
        s3_access_key: Optional[str] = None,
        s3_bucket_name: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
        s3_region: Optional[str] = None,
        s3_secret_key: Optional[str] = None,
        s3_session_token: Optional[str] = None,
    ) -> Dict:
        """Update an existing cloud storage integration.

        This method allows you to modify the configuration of an existing cloud storage
        integration, including credentials, access restrictions, and other settings.
        Only specified parameters will be updated; omitted parameters remain unchanged.

        Args:
            integration_id: ID of the cloud storage integration to update.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_projects: List of project IDs allowed to use this integration.
            aws_access_point_arn: AWS access point ARN for VPC endpoint access.
            aws_role_arn: AWS IAM role ARN for cross-account access.
            aws_role_external_id: AWS role external ID for additional security.
            azure_connection_url: Azure Storage connection URL.
            azure_is_using_service_credentials: Whether Azure uses service credentials.
            azure_sas_token: Azure Shared Access Signature token.
            azure_tenant_id: Azure tenant ID for multi-tenant applications.
            gcp_bucket_name: Google Cloud Storage bucket name.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.
            name: Updated name of the cloud storage integration.
            organization_id: Organization ID (usually not changed).
            platform: Platform of the cloud storage integration (usually not changed).
            status: Status of the cloud storage integration.
            s3_access_key: S3-compatible access key for authentication.
            s3_bucket_name: S3 bucket name for AWS or S3-compatible storage.
            s3_endpoint: S3 endpoint URL for custom S3-compatible services.
            s3_region: S3 region for AWS S3 buckets.
            s3_secret_key: S3-compatible secret key for authentication.
            s3_session_token: S3 session token for temporary credentials.

        Returns:
            A dictionary containing the updated integration information.

        Raises:
            ValueError: If integration_id is invalid or empty.
            RuntimeError: If the integration cannot be updated due to invalid credentials
                         or configuration errors.
            Exception: If an unexpected error occurs during integration update.

        Examples:
            >>> # Update integration name
            >>> result = kili.integrations.update(
            ...     integration_id="integration_123",
            ...     name="Updated Integration Name"
            ... )

            >>> # Update access restrictions
            >>> result = kili.integrations.update(
            ...     integration_id="integration_123",
            ...     allowed_paths=["/datasets/training", "/datasets/validation"],
            ...     allowed_projects=["project_456", "project_789"]
            ... )

            >>> # Update AWS credentials
            >>> result = kili.integrations.update(
            ...     integration_id="integration_123",
            ...     s3_access_key="NEW_ACCESS_KEY",
            ...     s3_secret_key="NEW_SECRET_KEY"
            ... )

            >>> # Update Azure configuration
            >>> result = kili.integrations.update(
            ...     integration_id="integration_123",
            ...     azure_sas_token="sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=..."
            ... )
        """
        # Validate input parameters
        if not integration_id or not integration_id.strip():
            raise ValueError("integration_id cannot be empty or None")

        # Access the legacy method directly by calling it from the mixin class
        try:
            return CloudStorageClientMethods.update_cloud_storage_integration(
                self.client,
                cloud_storage_integration_id=integration_id,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                aws_access_point_arn=aws_access_point_arn,
                aws_role_arn=aws_role_arn,
                aws_role_external_id=aws_role_external_id,
                azure_connection_url=azure_connection_url,
                azure_is_using_service_credentials=azure_is_using_service_credentials,
                azure_sas_token=azure_sas_token,
                azure_tenant_id=azure_tenant_id,
                gcp_bucket_name=gcp_bucket_name,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
                name=name,
                organization_id=organization_id,
                platform=platform,
                s3_access_key=s3_access_key,
                s3_bucket_name=s3_bucket_name,
                s3_endpoint=s3_endpoint,
                s3_region=s3_region,
                s3_secret_key=s3_secret_key,
                s3_session_token=s3_session_token,
                status=status,
            )
        except Exception as e:
            # Enhanced error handling for update failures
            if "not found" in str(e).lower():
                raise RuntimeError(
                    f"Update failed: Integration '{integration_id}' not found. "
                    f"Please verify the integration ID is correct. Details: {e!s}"
                ) from e
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Update failed: Invalid credentials for integration '{integration_id}'. "
                    f"Please verify your authentication parameters. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Update failed: Insufficient permissions to modify integration "
                    f"'{integration_id}'. Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def delete(self, integration_id: str) -> str:
        """Delete a cloud storage integration.

        This method permanently removes a cloud storage integration from your organization.
        Any connections using this integration will be disconnected, and projects will
        lose access to the associated cloud storage.

        Warning:
            This operation is irreversible. Ensure that no active projects depend on
            this integration before deletion.

        Args:
            integration_id: ID of the cloud storage integration to delete.

        Returns:
            The ID of the deleted integration.

        Raises:
            ValueError: If integration_id is invalid or empty.
            RuntimeError: If the integration cannot be deleted due to active connections
                         or insufficient permissions.
            Exception: If an unexpected error occurs during integration deletion.

        Examples:
            >>> # Delete an integration
            >>> deleted_id = kili.integrations.delete("integration_123")

            >>> # Verify deletion by checking it no longer exists
            >>> try:
            ...     kili.integrations.list(integration_id="integration_123")
            ... except RuntimeError:
            ...     print("Integration successfully deleted")
        """
        # Validate input parameters
        if not integration_id or not integration_id.strip():
            raise ValueError("integration_id cannot be empty or None")

        # Access the legacy method directly by calling it from the mixin class
        try:
            return CloudStorageClientMethods.delete_cloud_storage_integration(
                self.client,
                cloud_storage_integration_id=integration_id,
            )
        except Exception as e:
            # Enhanced error handling for deletion failures
            if "not found" in str(e).lower():
                raise RuntimeError(
                    f"Deletion failed: Integration '{integration_id}' not found. "
                    f"Please verify the integration ID is correct. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Deletion failed: Insufficient permissions to delete integration "
                    f"'{integration_id}'. Details: {e!s}"
                ) from e
            if "active" in str(e).lower() or "connection" in str(e).lower():
                raise RuntimeError(
                    f"Deletion failed: Integration '{integration_id}' has active connections "
                    f"or is being used by projects. Please remove all connections before "
                    f"deletion. Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise
