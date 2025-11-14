"""Storages domain namespace for the Kili Python SDK."""
# pylint: disable=too-many-lines

from functools import cached_property
from typing import Dict, Generator, List, Optional, TypedDict

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.cloud_storage import DataIntegrationPlatform, DataIntegrationStatus
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods


class IntegrationFilter(TypedDict, total=False):
    """Filter parameters for querying cloud storage integrations.

    Attributes:
        integration_id: Filter by integration ID.
        name: Filter by integration name.
        platform: Filter by platform type (AWS, Azure, GCP, CustomS3).
        status: Filter by connection status (CONNECTED, DISCONNECTED, CHECKING).
        organization_id: Filter by organization ID.
    """

    integration_id: Optional[str]
    name: Optional[str]
    platform: Optional[DataIntegrationPlatform]
    status: Optional[DataIntegrationStatus]
    organization_id: Optional[str]


class IntegrationsNamespace:
    """Nested namespace for cloud storage integration operations."""

    def __init__(self, client):
        """Initialize the integrations namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @deprecated(
        "'storages.integrations' is a namespace, not a callable method. "
        "Use kili.storages.integrations.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.storages.integrations.{m}()" for m in available_methods)
        raise TypeError(
            f"'storages.integrations' is a namespace, not a callable method. "
            f"The domain API provides methods for integration operations.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.storages.integrations.list()"
        )

    @typechecked
    def list(
        self,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[IntegrationFilter] = None,
    ) -> List[Dict]:
        """Get a list of cloud storage integrations that match a set of criteria.

        This method provides a simplified interface for querying cloud storage integrations,
        making it easier to discover and manage external service integrations configured
        in your organization.

        Args:
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
            filter: Optional filters for integrations. See IntegrationFilter for available fields:
                integration_id, name, platform, status, organization_id.

        Returns:
            A list of cloud storage integrations matching the criteria.

        Examples:
            >>> # List all integrations
            >>> integrations = kili.storages.integrations.list()

            >>> # Get a specific integration
            >>> integration = kili.storages.integrations.list(
            ...     filter={"integration_id": "integration_123"}
            ... )

            >>> # List AWS integrations only
            >>> aws_integrations = kili.storages.integrations.list(
            ...     filter={"platform": "AWS"}
            ... )

            >>> # List integrations with custom fields
            >>> integrations = kili.storages.integrations.list(
            ...     fields=["id", "name", "platform", "allowedPaths"]
            ... )

            >>> # List integrations with pagination
            >>> first_page = kili.storages.integrations.list(first=10, skip=0)
        """
        filter_dict = filter or {}

        return self._client.cloud_storage_integrations(
            cloud_storage_integration_id=filter_dict.get("integration_id"),
            name=filter_dict.get("name"),
            platform=filter_dict.get("platform"),
            status=filter_dict.get("status"),
            organization_id=filter_dict.get("organization_id"),
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=False,
        )

    @typechecked
    def list_as_generator(
        self,
        fields: ListOrTuple[str] = ("name", "id", "platform", "status"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[IntegrationFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of cloud storage integrations that match a set of criteria.

        This method provides a simplified interface for querying cloud storage integrations,
        making it easier to discover and manage external service integrations configured
        in your organization.

        Args:
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
            filter: Optional filters for integrations. See IntegrationFilter for available fields:
                integration_id, name, platform, status, organization_id.

        Returns:
            A generator yielding cloud storage integrations matching the criteria.

        Examples:
            >>> # Get integrations as generator
            >>> for integration in kili.storages.integrations.list_as_generator():
            ...     print(integration["name"])
        """
        filter_dict = filter or {}

        return self._client.cloud_storage_integrations(
            cloud_storage_integration_id=filter_dict.get("integration_id"),
            name=filter_dict.get("name"),
            platform=filter_dict.get("platform"),
            status=filter_dict.get("status"),
            organization_id=filter_dict.get("organization_id"),
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=True,
        )

    @typechecked
    def count(
        self,
        filter: Optional[IntegrationFilter] = None,
    ) -> int:
        """Count and return the number of cloud storage integrations that match a set of criteria.

        This method provides a convenient way to count integrations without retrieving
        the full data, useful for pagination and analytics.

        Args:
            filter: Optional filters for integrations. See IntegrationFilter for available fields:
                integration_id, name, platform, status, organization_id.

        Returns:
            The number of cloud storage integrations that match the criteria.

        Examples:
            >>> # Count all integrations
            >>> total = kili.storages.integrations.count()

            >>> # Count AWS integrations
            >>> aws_count = kili.storages.integrations.count(
            ...     filter={"platform": "AWS"}
            ... )

            >>> # Count connected integrations
            >>> connected_count = kili.storages.integrations.count(
            ...     filter={"status": "CONNECTED"}
            ... )

            >>> # Count integrations by name pattern
            >>> prod_count = kili.storages.integrations.count(
            ...     filter={"name": "Production*"}
            ... )
        """
        filter_dict = filter or {}

        return self._client.count_cloud_storage_integrations(
            cloud_storage_integration_id=filter_dict.get("integration_id"),
            name=filter_dict.get("name"),
            platform=filter_dict.get("platform"),
            status=filter_dict.get("status"),
            organization_id=filter_dict.get("organization_id"),
        )

    @typechecked
    def create_aws(
        self,
        bucket_name: str,
        region: str,
        name: str,
        fields: ListOrTuple[str] = (
            "id",
            "name",
            "status",
            "platform",
            "allowedPaths",
        ),
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        session_token: Optional[str] = None,
        access_point_arn: Optional[str] = None,
        role_arn: Optional[str] = None,
        role_external_id: Optional[str] = None,
        allowed_path: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_project: Optional[str] = None,
        allowed_projects: Optional[List[str]] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
    ) -> Dict:
        """Create a new AWS S3 cloud storage integration.

        This method creates an integration with Amazon S3, enabling your organization
        to connect Kili projects to S3 buckets for asset storage and synchronization.

        Args:
            bucket_name: S3 bucket name.
            region: AWS region (e.g., 'us-east-1', 'eu-west-1').
            name: Name for this integration.
            fields: All the fields to request among the possible fields for the integration.
                Available fields include: id, name, status, platform, allowedPaths, etc.
            access_key: AWS access key for authentication (optional if using IAM roles).
            secret_key: AWS secret key for authentication (optional if using IAM roles).
            session_token: AWS session token for temporary credentials.
            access_point_arn: AWS access point ARN for VPC endpoint access.
            role_arn: AWS IAM role ARN for cross-account access.
            role_external_id: AWS role external ID for additional security.
            allowed_path: Allowed path for restricting access within the storage.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_project: Project ID allowed to use this integration.
            allowed_projects: List of project IDs allowed to use this integration.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.

        Returns:
            A dictionary containing the created integration information.

        Raises:
            ValueError: If required parameters are missing or invalid.
            RuntimeError: If the integration cannot be created due to invalid credentials
                         or S3 bucket access issues.
            Exception: If an unexpected error occurs during integration creation.

        Examples:
            >>> # Create AWS S3 integration with access keys
            >>> result = kili.storages.integrations.create_aws(
            ...     bucket_name="my-production-bucket",
            ...     region="us-east-1",
            ...     name="Production S3 Bucket",
            ...     access_key="AKIAIOSFODNN7EXAMPLE",
            ...     secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            ... )

            >>> # Create AWS S3 integration with IAM role
            >>> result = kili.storages.integrations.create_aws(
            ...     bucket_name="my-bucket",
            ...     region="us-west-2",
            ...     name="S3 via IAM Role",
            ...     role_arn="arn:aws:iam::123456789012:role/KiliS3Access",
            ...     role_external_id="unique-external-id"
            ... )

            >>> # Create with access restrictions
            >>> result = kili.storages.integrations.create_aws(
            ...     bucket_name="shared-bucket",
            ...     region="us-east-1",
            ...     name="Shared S3 Storage",
            ...     access_key="AKIAIOSFODNN7EXAMPLE",
            ...     secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            ...     allowed_paths=["/datasets", "/models"]
            ... )

            >>> # Access the integration ID
            >>> integration_id = result["id"]
        """
        # Convert singular to plural
        if allowed_path is not None:
            allowed_paths = [allowed_path]
        if allowed_project is not None:
            allowed_projects = [allowed_project]

        # Validate input parameters
        if not name or not name.strip():
            raise ValueError("name cannot be empty or None")

        if not bucket_name or not bucket_name.strip():
            raise ValueError("bucket_name cannot be empty or None")

        if not region or not region.strip():
            raise ValueError("region cannot be empty or None")

        try:
            return self._create(
                platform="AWS",
                name=name,
                fields=fields,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                aws_access_point_arn=access_point_arn,
                aws_role_arn=role_arn,
                aws_role_external_id=role_external_id,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
                s3_access_key=access_key,
                s3_bucket_name=bucket_name,
                s3_region=region,
                s3_secret_key=secret_key,
                s3_session_token=session_token,
            )
        except Exception as e:
            # Enhanced error handling for AWS-specific failures
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create AWS integration '{name}': Invalid credentials. "
                    f"Please verify your AWS access key and secret key. "
                    f"Details: {e!s}"
                ) from e
            if "bucket" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create AWS integration '{name}': S3 bucket '{bucket_name}' "
                    f"not found or inaccessible in region '{region}'. "
                    f"Please verify the bucket name, region, and permissions. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create AWS integration '{name}': Insufficient permissions "
                    f"to access S3 bucket '{bucket_name}'. Please verify your IAM permissions. "
                    f"Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def create_azure(
        self,
        connection_url: str,
        name: str,
        fields: ListOrTuple[str] = (
            "id",
            "name",
            "status",
            "platform",
            "allowedPaths",
        ),
        sas_token: Optional[str] = None,
        is_using_service_credentials: Optional[bool] = None,
        tenant_id: Optional[str] = None,
        allowed_path: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_project: Optional[str] = None,
        allowed_projects: Optional[List[str]] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
    ) -> Dict:
        """Create a new Azure Blob Storage cloud storage integration.

        This method creates an integration with Azure Blob Storage, enabling your organization
        to connect Kili projects to Azure storage accounts for asset storage and synchronization.

        Args:
            connection_url: Azure Storage connection URL.
            name: Name for this integration.
            fields: All the fields to request among the possible fields for the integration.
                Available fields include: id, name, status, platform, allowedPaths, etc.
            sas_token: Azure Shared Access Signature token.
            is_using_service_credentials: Whether Azure uses service credentials.
            tenant_id: Azure tenant ID for multi-tenant applications.
            allowed_path: Allowed path for restricting access within the storage.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_project: Project ID allowed to use this integration.
            allowed_projects: List of project IDs allowed to use this integration.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.

        Returns:
            A dictionary containing the created integration information.

        Raises:
            ValueError: If required parameters are missing or invalid.
            RuntimeError: If the integration cannot be created due to invalid credentials
                         or Azure storage access issues.
            Exception: If an unexpected error occurs during integration creation.

        Examples:
            >>> # Create Azure Blob Storage integration with SAS token
            >>> result = kili.storages.integrations.create_azure(
            ...     connection_url="https://myaccount.blob.core.windows.net/",
            ...     name="Azure Production Storage",
            ...     sas_token="sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=..."
            ... )

            >>> # Create Azure integration with service credentials
            >>> result = kili.storages.integrations.create_azure(
            ...     connection_url="https://myaccount.blob.core.windows.net/",
            ...     name="Azure Dev Storage",
            ...     is_using_service_credentials=True,
            ...     tenant_id="XXX"
            ... )

            >>> # Create with access restrictions
            >>> result = kili.storages.integrations.create_azure(
            ...     connection_url="https://myaccount.blob.core.windows.net/",
            ...     name="Shared Azure Storage",
            ...     sas_token="sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=...",
            ...     allowed_paths=["/datasets", "/models"]
            ... )

            >>> # Access the integration ID
            >>> integration_id = result["id"]
        """
        # Convert singular to plural
        if allowed_path is not None:
            allowed_paths = [allowed_path]
        if allowed_project is not None:
            allowed_projects = [allowed_project]

        # Validate input parameters
        if not name or not name.strip():
            raise ValueError("name cannot be empty or None")

        if not connection_url or not connection_url.strip():
            raise ValueError("connection_url cannot be empty or None")

        try:
            return self._create(
                platform="Azure",
                name=name,
                fields=fields,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                azure_connection_url=connection_url,
                azure_is_using_service_credentials=is_using_service_credentials,
                azure_sas_token=sas_token,
                azure_tenant_id=tenant_id,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
            )
        except Exception as e:
            # Enhanced error handling for Azure-specific failures
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create Azure integration '{name}': Invalid credentials. "
                    f"Please verify your Azure SAS token or service credentials. "
                    f"Details: {e!s}"
                ) from e
            if "container" in str(e).lower() or "storage" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create Azure integration '{name}': Storage account or "
                    f"container not found or inaccessible at '{connection_url}'. "
                    f"Please verify the connection URL and permissions. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create Azure integration '{name}': Insufficient permissions "
                    f"to access Azure storage. Please verify your access rights. "
                    f"Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def create_gcp(
        self,
        bucket_name: str,
        name: str,
        fields: ListOrTuple[str] = (
            "id",
            "name",
            "status",
            "platform",
            "allowedPaths",
        ),
        allowed_path: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_project: Optional[str] = None,
        allowed_projects: Optional[List[str]] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
    ) -> Dict:
        """Create a new Google Cloud Storage cloud storage integration.

        This method creates an integration with Google Cloud Storage, enabling your organization
        to connect Kili projects to GCS buckets for asset storage and synchronization.

        Args:
            bucket_name: Google Cloud Storage bucket name.
            name: Name for this integration.
            fields: All the fields to request among the possible fields for the integration.
                Available fields include: id, name, status, platform, allowedPaths, etc.
            allowed_path: Allowed path for restricting access within the storage.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_project: Project ID allowed to use this integration.
            allowed_projects: List of project IDs allowed to use this integration.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.

        Returns:
            A dictionary containing the created integration information.

        Raises:
            ValueError: If required parameters are missing or invalid.
            RuntimeError: If the integration cannot be created due to invalid credentials
                         or GCS bucket access issues.
            Exception: If an unexpected error occurs during integration creation.

        Examples:
            >>> # Create GCP Cloud Storage integration
            >>> result = kili.storages.integrations.create_gcp(
            ...     bucket_name="my-gcp-bucket",
            ...     name="GCP Production Bucket"
            ... )

            >>> # Create with access restrictions
            >>> result = kili.storages.integrations.create_gcp(
            ...     bucket_name="shared-gcp-bucket",
            ...     name="Shared GCP Storage",
            ...     allowed_paths=["/datasets", "/models"]
            ... )

            >>> # Create with specific projects allowed
            >>> result = kili.storages.integrations.create_gcp(
            ...     bucket_name="my-gcp-bucket",
            ...     name="Project-specific GCS",
            ...     allowed_projects=["project_123", "project_456"]
            ... )

            >>> # Access the integration ID
            >>> integration_id = result["id"]
        """
        # Convert singular to plural
        if allowed_path is not None:
            allowed_paths = [allowed_path]
        if allowed_project is not None:
            allowed_projects = [allowed_project]

        # Validate input parameters
        if not name or not name.strip():
            raise ValueError("name cannot be empty or None")

        if not bucket_name or not bucket_name.strip():
            raise ValueError("bucket_name cannot be empty or None")

        try:
            return self._create(
                platform="GCP",
                name=name,
                fields=fields,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                gcp_bucket_name=bucket_name,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
            )
        except Exception as e:
            # Enhanced error handling for GCP-specific failures
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create GCP integration '{name}': Invalid credentials. "
                    f"Please verify your Google Cloud service account configuration. "
                    f"Details: {e!s}"
                ) from e
            if "bucket" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create GCP integration '{name}': Cloud Storage bucket "
                    f"'{bucket_name}' not found or inaccessible. "
                    f"Please verify the bucket name and permissions. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create GCP integration '{name}': Insufficient permissions "
                    f"to access Cloud Storage bucket '{bucket_name}'. "
                    f"Please verify your IAM permissions. Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def create_s3(
        self,
        endpoint: str,
        bucket_name: str,
        name: str,
        fields: ListOrTuple[str] = (
            "id",
            "name",
            "status",
            "platform",
            "allowedPaths",
        ),
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        session_token: Optional[str] = None,
        region: Optional[str] = None,
        allowed_path: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_project: Optional[str] = None,
        allowed_projects: Optional[List[str]] = None,
        include_root_files: Optional[str] = None,
        internal_processing_authorized: Optional[str] = None,
    ) -> Dict:
        """Create a new custom S3-compatible cloud storage integration.

        This method creates an integration with custom S3-compatible storage services
        (e.g., MinIO, Ceph, Wasabi), enabling your organization to connect Kili projects
        to S3-compatible buckets for asset storage and synchronization.

        Args:
            endpoint: S3 endpoint URL for custom S3-compatible services.
            bucket_name: S3 bucket name.
            name: Name for this integration.
            fields: All the fields to request among the possible fields for the integration.
                Available fields include: id, name, status, platform, allowedPaths, etc.
            access_key: S3-compatible access key for authentication.
            secret_key: S3-compatible secret key for authentication.
            session_token: S3 session token for temporary credentials.
            region: S3 region (optional for custom S3 services).
            allowed_path: Allowed path for restricting access within the storage.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_project: Project ID allowed to use this integration.
            allowed_projects: List of project IDs allowed to use this integration.
            include_root_files: Whether to include files in the storage root.
            internal_processing_authorized: Whether internal processing is authorized.

        Returns:
            A dictionary containing the created integration information.

        Raises:
            ValueError: If required parameters are missing or invalid.
            RuntimeError: If the integration cannot be created due to invalid credentials
                         or bucket access issues.
            Exception: If an unexpected error occurs during integration creation.

        Examples:
            >>> # Create MinIO integration
            >>> result = kili.storages.integrations.create_s3(
            ...     endpoint="http://localhost:9000",
            ...     bucket_name="dev-bucket",
            ...     name="MinIO Development Storage",
            ...     access_key="minioadmin",
            ...     secret_key="minioadmin"
            ... )

            >>> # Create Wasabi integration
            >>> result = kili.storages.integrations.create_s3(
            ...     endpoint="https://s3.wasabisys.com",
            ...     bucket_name="my-wasabi-bucket",
            ...     name="Wasabi Storage",
            ...     region="us-east-1",
            ...     access_key="WASABI_ACCESS_KEY",
            ...     secret_key="WASABI_SECRET_KEY"
            ... )

            >>> # Create with access restrictions
            >>> result = kili.storages.integrations.create_s3(
            ...     endpoint="http://minio.example.com:9000",
            ...     bucket_name="shared-bucket",
            ...     name="MinIO Shared Storage",
            ...     access_key="access_key",
            ...     secret_key="secret_key",
            ...     allowed_paths=["/datasets", "/models"]
            ... )

            >>> # Access the integration ID
            >>> integration_id = result["id"]
        """
        # Convert singular to plural
        if allowed_path is not None:
            allowed_paths = [allowed_path]
        if allowed_project is not None:
            allowed_projects = [allowed_project]

        # Validate input parameters
        if not name or not name.strip():
            raise ValueError("name cannot be empty or None")

        if not endpoint or not endpoint.strip():
            raise ValueError("endpoint cannot be empty or None")

        if not bucket_name or not bucket_name.strip():
            raise ValueError("bucket_name cannot be empty or None")

        try:
            return self._create(
                platform="CustomS3",
                name=name,
                fields=fields,
                allowed_paths=allowed_paths,
                allowed_projects=allowed_projects,
                s3_access_key=access_key,
                s3_bucket_name=bucket_name,
                s3_endpoint=endpoint,
                s3_region=region,
                s3_secret_key=secret_key,
                s3_session_token=session_token,
                include_root_files=include_root_files,
                internal_processing_authorized=internal_processing_authorized,
            )
        except Exception as e:
            # Enhanced error handling for custom S3-specific failures
            if "credential" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create custom S3 integration '{name}': Invalid credentials. "
                    f"Please verify your S3-compatible access key and secret key for endpoint "
                    f"'{endpoint}'. Details: {e!s}"
                ) from e
            if "bucket" in str(e).lower() or "endpoint" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create custom S3 integration '{name}': Bucket '{bucket_name}' "
                    f"not found or endpoint '{endpoint}' is inaccessible. "
                    f"Please verify the endpoint URL, bucket name, and network connectivity. "
                    f"Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create custom S3 integration '{name}': Insufficient permissions "
                    f"to access bucket '{bucket_name}' at endpoint '{endpoint}'. "
                    f"Please verify your access rights. Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    def _create(
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
        """Internal method to create a cloud storage integration.

        This is a private method called by platform-specific public methods.
        Use create_aws(), create_azure(), create_gcp(), or create_s3() instead.
        """
        return self._client.create_cloud_storage_integration(
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

    @typechecked
    def update(
        self,
        integration_id: str,
        allowed_path: Optional[str] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_project: Optional[str] = None,
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
            allowed_path: Allowed path for restricting access within the storage.
            allowed_paths: List of allowed paths for restricting access within the storage.
            allowed_project: Project ID allowed to use this integration.
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
            >>> result = kili.storages.integrations.update(
            ...     integration_id="integration_123",
            ...     name="Updated Integration Name"
            ... )

            >>> # Update access restrictions
            >>> result = kili.storages.integrations.update(
            ...     integration_id="integration_123",
            ...     allowed_paths=["/datasets/training", "/datasets/validation"],
            ...     allowed_projects=["project_456", "project_789"]
            ... )

            >>> # Update AWS credentials
            >>> result = kili.storages.integrations.update(
            ...     integration_id="integration_123",
            ...     s3_access_key="NEW_ACCESS_KEY",
            ...     s3_secret_key="NEW_SECRET_KEY"
            ... )

            >>> # Update Azure configuration
            >>> result = kili.storages.integrations.update(
            ...     integration_id="integration_123",
            ...     azure_sas_token="sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=..."
            ... )
        """
        # Convert singular to plural
        if allowed_path is not None:
            allowed_paths = [allowed_path]
        if allowed_project is not None:
            allowed_projects = [allowed_project]

        # Validate input parameters
        if not integration_id or not integration_id.strip():
            raise ValueError("integration_id cannot be empty or None")

        try:
            return self._client.update_cloud_storage_integration(
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
            >>> deleted_id = kili.storages.integrations.delete("integration_123")

            >>> # Verify deletion by checking it no longer exists
            >>> try:
            ...     kili.storages.integrations.list(integration_id="integration_123")
            ... except RuntimeError:
            ...     print("Integration successfully deleted")
        """
        # Validate input parameters
        if not integration_id or not integration_id.strip():
            raise ValueError("integration_id cannot be empty or None")

        try:
            return self._client.delete_cloud_storage_integration(
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


class ConnectionFilter(TypedDict, total=False):
    """Filter parameters for querying cloud storage connections.

    Attributes:
        connection_id: Filter by connection ID.
        integration_id: Filter by cloud storage integration ID.
        project_id: Filter by project ID.
    """

    connection_id: Optional[str]
    integration_id: Optional[str]
    project_id: Optional[str]


class ConnectionsNamespace:
    """Nested namespace for cloud storage connection operations."""

    def __init__(self, client):
        """Initialize the connections namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @deprecated(
        "'storages.connections' is a namespace, not a callable method. "
        "Use kili.storages.connections.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.storages.connections.{m}()" for m in available_methods)
        raise TypeError(
            f"'storages.connections' is a namespace, not a callable method. "
            f"The domain API provides methods for connection operations.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.storages.connections.list(project_id='...')"
        )

    @typechecked
    def list(
        self,
        fields: ListOrTuple[str] = (
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[ConnectionFilter] = None,
    ) -> List[Dict]:
        """Get a list of cloud storage connections that match a set of criteria.

        This method provides a simplified interface for querying cloud storage connections,
        making it easier to discover and manage connections between cloud storage integrations
        and projects.

        Args:
            fields: All the fields to request among the possible fields for the connections.
                Available fields include:
                - id: Connection identifier
                - lastChecked: Timestamp of last synchronization check
                - numberOfAssets: Number of assets in the connection
                - selectedFolders: List of folders selected for synchronization
                - projectId: Associated project identifier
                See the documentation for all possible fields.
            first: Maximum number of connections to return.
            skip: Number of connections to skip (ordered by creation date).
            disable_tqdm: If True, the progress bar will be disabled.
            filter: Optional filters for connections. See ConnectionFilter for available fields:
                connection_id, cloud_storage_integration_id, project_id.

        Returns:
            A list of cloud storage connections matching the criteria.

        Examples:
            >>> # List all connections for a project
            >>> connections = kili.storages.connections.list(
            ...     filter={"project_id": "project_123"}
            ... )

            >>> # Get a specific connection
            >>> connection = kili.storages.connections.list(
            ...     filter={"connection_id": "connection_789"}
            ... )

            >>> # List connections for a cloud storage integration
            >>> connections = kili.storages.connections.list(
            ...     filter={"cloud_storage_integration_id": "integration_456"}
            ... )

            >>> # List with custom fields
            >>> connections = kili.storages.connections.list(
            ...     filter={"project_id": "project_123"},
            ...     fields=["id", "numberOfAssets", "lastChecked"]
            ... )
        """
        filter_dict = filter or {}

        return self._client.cloud_storage_connections(
            cloud_storage_connection_id=filter_dict.get("connection_id"),
            cloud_storage_integration_id=filter_dict.get("cloud_storage_integration_id"),
            project_id=filter_dict.get("project_id"),
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=False,
        )

    @typechecked
    def list_as_generator(
        self,
        fields: ListOrTuple[str] = (
            "id",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "projectId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[ConnectionFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of cloud storage connections that match a set of criteria.

        This method provides a simplified interface for querying cloud storage connections,
        making it easier to discover and manage connections between cloud storage integrations
        and projects.

        Args:
            fields: All the fields to request among the possible fields for the connections.
                Available fields include:
                - id: Connection identifier
                - lastChecked: Timestamp of last synchronization check
                - numberOfAssets: Number of assets in the connection
                - selectedFolders: List of folders selected for synchronization
                - projectId: Associated project identifier
                See the documentation for all possible fields.
            first: Maximum number of connections to return.
            skip: Number of connections to skip (ordered by creation date).
            disable_tqdm: If True, the progress bar will be disabled.
            filter: Optional filters for connections. See ConnectionFilter for available fields:
                connection_id, cloud_storage_integration_id, project_id.

        Returns:
            A generator yielding cloud storage connections matching the criteria.

        Examples:
            >>> # Get connections as generator
            >>> for conn in kili.storages.connections.list_as_generator(
            ...     filter={"project_id": "project_123"}
            ... ):
            ...     print(conn["id"])
        """
        filter_dict = filter or {}

        return self._client.cloud_storage_connections(
            cloud_storage_connection_id=filter_dict.get("connection_id"),
            cloud_storage_integration_id=filter_dict.get("cloud_storage_integration_id"),
            project_id=filter_dict.get("project_id"),
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=True,
        )

    @typechecked
    def create(
        self,
        project_id: str,
        cloud_storage_integration_id: str,
        selected_folder: Optional[str] = None,
        selected_folders: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> Dict:
        """Connect a cloud storage integration to a project.

        This method creates a new connection between a cloud storage integration and a project,
        enabling the project to synchronize assets from the cloud storage. It provides
        comprehensive filtering options to control which assets are synchronized.

        Args:
            project_id: ID of the project to connect the cloud storage to.
            cloud_storage_integration_id: ID of the cloud storage integration to connect.
            selected_folder: Specific folder to connect from the cloud storage.
                This parameter is deprecated and will be removed in future versions.
                Use prefix, include, and exclude parameters instead.
            selected_folders: List of specific folders to connect from the cloud storage.
                This parameter is deprecated and will be removed in future versions.
                Use prefix, include, and exclude parameters instead.
            prefix: Filter files to synchronize based on their base path.
                Only files with paths starting with this prefix will be considered.
            include: List of glob patterns to include files based on their path.
                Files matching any of these patterns will be included.
            exclude: List of glob patterns to exclude files based on their path.
                Files matching any of these patterns will be excluded.

        Returns:
            A dictionary containing the ID of the created connection.

        Raises:
            ValueError: If project_id or cloud_storage_integration_id are invalid.
            RuntimeError: If the connection cannot be established.
            Exception: If an unexpected error occurs during connection creation.

        Examples:
            >>> # Basic connection setup
            >>> result = kili.storages.connections.create(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456"
            ... )

            >>> # Connect with path prefix filter
            >>> result = kili.storages.connections.create(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     prefix="datasets/training/"
            ... )

            >>> # Connect with include/exclude patterns
            >>> result = kili.storages.connections.create(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     include=["*.jpg", "*.png", "*.jpeg"],
            ...     exclude=["**/temp/*", "**/backup/*"]
            ... )

            >>> # Advanced filtering combination
            >>> result = kili.storages.connections.create(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     prefix="data/images/",
            ...     include=["*.jpg", "*.png"],
            ...     exclude=["*/thumbnails/*"]
            ... )

            >>> # Access the connection ID
            >>> connection_id = result["id"]
        """
        # Convert singular to plural
        if selected_folder is not None:
            selected_folders = [selected_folder]

        # Validate input parameters
        if not project_id or not project_id.strip():
            raise ValueError("project_id cannot be empty or None")

        if not cloud_storage_integration_id or not cloud_storage_integration_id.strip():
            raise ValueError("cloud_storage_integration_id cannot be empty or None")

        try:
            return self._client.add_cloud_storage_connection(
                project_id=project_id,
                cloud_storage_integration_id=cloud_storage_integration_id,
                selected_folders=selected_folders,
                prefix=prefix,
                include=include,
                exclude=exclude,
            )
        except Exception as e:
            # Enhance error messaging for connection failures
            if "not found" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create connection: Project '{project_id}' or "
                    f"integration '{cloud_storage_integration_id}' not found. "
                    f"Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Failed to create connection: Insufficient permissions to access "
                    f"project '{project_id}' or integration '{cloud_storage_integration_id}'. "
                    f"Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    @typechecked
    def sync(
        self,
        connection_id: str,
        delete_extraneous_files: bool = False,
        dry_run: bool = False,
    ) -> Dict:
        """Synchronize a cloud storage connection.

        This method synchronizes the specified cloud storage connection by computing
        differences between the cloud storage and the project, then applying those changes.
        It provides safety features like dry-run mode and optional deletion of extraneous files.

        Args:
            connection_id: ID of the cloud storage connection to synchronize.
            delete_extraneous_files: If True, delete files that exist in the project
                but are no longer present in the cloud storage. Use with caution.
            dry_run: If True, performs a simulation without making actual changes.
                Useful for previewing what changes would be made before applying them.

        Returns:
            A dictionary containing connection information after synchronization,
            including the number of assets and project ID.

        Raises:
            ValueError: If connection_id is invalid or empty.
            RuntimeError: If synchronization fails due to permissions or connectivity issues.
            Exception: If an unexpected error occurs during synchronization.

        Examples:
            >>> # Basic synchronization
            >>> result = kili.storages.connections.sync(connection_id="connection_789")

            >>> # Dry-run to preview changes
            >>> preview = kili.storages.connections.sync(
            ...     connection_id="connection_789",
            ...     dry_run=True
            ... )

            >>> # Full synchronization with cleanup
            >>> result = kili.storages.connections.sync(
            ...     connection_id="connection_789",
            ...     delete_extraneous_files=True,
            ...     dry_run=False
            ... )

            >>> # Check results
            >>> assets_count = result["numberOfAssets"]
            >>> project_id = result["projectId"]
        """
        # Validate input parameters
        if not connection_id or not connection_id.strip():
            raise ValueError("connection_id cannot be empty or None")

        try:
            return self._client.synchronize_cloud_storage_connection(
                cloud_storage_connection_id=connection_id,
                delete_extraneous_files=delete_extraneous_files,
                dry_run=dry_run,
            )
        except Exception as e:
            # Enhanced error handling for synchronization failures
            if "not found" in str(e).lower():
                raise RuntimeError(
                    f"Synchronization failed: Connection '{connection_id}' not found. "
                    f"Please verify the connection ID is correct. Details: {e!s}"
                ) from e
            if "permission" in str(e).lower() or "access" in str(e).lower():
                raise RuntimeError(
                    f"Synchronization failed: Insufficient permissions to access "
                    f"connection '{connection_id}' or its associated resources. "
                    f"Details: {e!s}"
                ) from e
            if "connectivity" in str(e).lower() or "network" in str(e).lower():
                raise RuntimeError(
                    f"Synchronization failed: Network connectivity issues with "
                    f"cloud storage for connection '{connection_id}'. "
                    f"Please check your cloud storage credentials and network connection. "
                    f"Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise


class StoragesNamespace(DomainNamespace):
    """Storages domain namespace providing cloud storage operations.

    This namespace provides access to all cloud storage functionality including
    integrations (connecting to external storage providers) and connections
    (linking integrations to projects).

    The namespace provides two nested namespaces:
    - integrations: Manage cloud storage integrations (AWS, Azure, GCP, CustomS3)
    - connections: Manage connections between integrations and projects

    Examples:
        >>> kili = Kili()
        >>> # List all integrations
        >>> integrations = kili.storages.integrations.list()

        >>> # Create a new AWS S3 integration
        >>> result = kili.storages.integrations.create(
        ...     platform="AWS",
        ...     name="My Production S3 Bucket",
        ...     s3_bucket_name="my-production-bucket",
        ...     s3_region="us-east-1",
        ...     s3_access_key="AKIAIOSFODNN7EXAMPLE",
        ...     s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        ... )

        >>> # List connections for a project
        >>> connections = kili.storages.connections.list(project_id="project_123")

        >>> # Add a new cloud storage connection
        >>> result = kili.storages.connections.add(
        ...     project_id="project_123",
        ...     cloud_storage_integration_id="integration_456",
        ...     prefix="data/images/",
        ...     include=["*.jpg", "*.png"]
        ... )

        >>> # Synchronize a connection
        >>> result = kili.storages.connections.sync(
        ...     connection_id="connection_789",
        ...     delete_extraneous_files=False
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the storages namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "storages")

    @deprecated(
        "'storages' is a namespace, not a callable method. "
        "Use kili.storages.integrations.list() or kili.storages.connections.list() instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where storages were accessed directly to the new domain API
        where they use nested namespaces.
        """
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The domain API provides nested namespaces for storage operations.\n"
            f"Available namespaces: kili.{self._domain_name}.integrations, kili.{self._domain_name}.connections\n"
            f"Examples:\n"
            f"  - List integrations: kili.{self._domain_name}.integrations.list()\n"
            f"  - List connections: kili.{self._domain_name}.connections.list(project_id='...')"
        )

    @cached_property
    def integrations(self) -> IntegrationsNamespace:
        """Get the integrations namespace for cloud storage integration operations.

        Returns:
            IntegrationsNamespace: Cloud storage integrations operations namespace
        """
        return IntegrationsNamespace(self._client)

    @cached_property
    def connections(self) -> ConnectionsNamespace:
        """Get the connections namespace for cloud storage connection operations.

        Returns:
            ConnectionsNamespace: Cloud storage connections operations namespace
        """
        return ConnectionsNamespace(self._client)
