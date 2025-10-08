"""Connections domain namespace for the Kili Python SDK."""

from typing import Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.connection import ConnectionView, validate_connection
from kili.domain_v2.project import IdResponse
from kili.presentation.client.cloud_storage import CloudStorageClientMethods


class ConnectionsNamespace(DomainNamespace):
    """Connections domain namespace providing cloud storage connection operations.

    This namespace provides access to all cloud storage connection functionality
    including listing, adding, and synchronizing cloud storage connections to projects.
    Cloud storage connections link cloud storage integrations to specific projects,
    allowing for simplified cloud storage workflows.

    The namespace provides the following main operations:
    - list(): Query and list cloud storage connections
    - add(): Connect a cloud storage integration to a project
    - sync(): Synchronize a cloud storage connection

    Examples:
        >>> kili = Kili()
        >>> # List connections for a specific project
        >>> connections = kili.connections.list(project_id="project_123")

        >>> # Add a new cloud storage connection
        >>> result = kili.connections.add(
        ...     project_id="project_123",
        ...     cloud_storage_integration_id="integration_456",
        ...     prefix="data/images/",
        ...     include=["*.jpg", "*.png"]
        ... )

        >>> # Synchronize a connection
        >>> result = kili.connections.sync(
        ...     connection_id="connection_789",
        ...     delete_extraneous_files=False
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the connections namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "connections")

    @overload
    def list(
        self,
        connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
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
        *,
        as_generator: Literal[True],
    ) -> Generator[ConnectionView, None, None]:
        ...

    @overload
    def list(
        self,
        connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
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
        *,
        as_generator: Literal[False] = False,
    ) -> List[ConnectionView]:
        ...

    @typechecked
    def list(
        self,
        connection_id: Optional[str] = None,
        cloud_storage_integration_id: Optional[str] = None,
        project_id: Optional[str] = None,
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
        *,
        as_generator: bool = False,
    ) -> Iterable[ConnectionView]:
        """Get a generator or a list of cloud storage connections that match a set of criteria.

        This method provides a simplified interface for querying cloud storage connections,
        making it easier to discover and manage connections between cloud storage integrations
        and projects.

        Args:
            connection_id: ID of a specific cloud storage connection to retrieve.
            cloud_storage_integration_id: ID of the cloud storage integration to filter by.
            project_id: ID of the project to filter connections by.
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
            as_generator: If True, a generator on the connections is returned.

        Returns:
            An iterable of cloud storage connections matching the criteria.

        Raises:
            ValueError: If none of connection_id, cloud_storage_integration_id,
                       or project_id is provided.

        Examples:
            >>> # List all connections for a project
            >>> connections = kili.connections.list(
            ...     project_id="project_123",
            ...     as_generator=False
            ... )

            >>> # Get a specific connection
            >>> connection = kili.connections.list(
            ...     connection_id="connection_789",
            ...     as_generator=False
            ... )

            >>> # List connections for a cloud storage integration
            >>> connections = kili.connections.list(
            ...     cloud_storage_integration_id="integration_456",
            ...     as_generator=False
            ... )

            >>> # List with custom fields
            >>> connections = kili.connections.list(
            ...     project_id="project_123",
            ...     fields=["id", "numberOfAssets", "lastChecked"],
            ...     as_generator=False
            ... )
        """
        # Access the legacy method directly by calling it from the mixin class
        result = CloudStorageClientMethods.cloud_storage_connections(
            self.client,
            cloud_storage_connection_id=connection_id,
            cloud_storage_integration_id=cloud_storage_integration_id,
            project_id=project_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Wrap results with ConnectionView
        if as_generator:
            # Create intermediate generator - iter() makes result explicitly iterable
            def _wrap_generator() -> Generator[ConnectionView, None, None]:
                result_iter = iter(result)
                for item in result_iter:
                    yield ConnectionView(validate_connection(item))

            return _wrap_generator()

        # Convert to list - list() makes result explicitly iterable
        result_list = list(result)
        return [ConnectionView(validate_connection(item)) for item in result_list]

    @typechecked
    def add(
        self,
        project_id: str,
        cloud_storage_integration_id: str,
        selected_folders: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> ConnectionView:
        """Connect a cloud storage integration to a project.

        This method creates a new connection between a cloud storage integration and a project,
        enabling the project to synchronize assets from the cloud storage. It provides
        comprehensive filtering options to control which assets are synchronized.

        Args:
            project_id: ID of the project to connect the cloud storage to.
            cloud_storage_integration_id: ID of the cloud storage integration to connect.
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
            A ConnectionView object representing the newly created connection.

        Raises:
            ValueError: If project_id or cloud_storage_integration_id are invalid.
            RuntimeError: If the connection cannot be established.
            Exception: If an unexpected error occurs during connection creation.

        Examples:
            >>> # Basic connection setup
            >>> connection = kili.connections.add(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456"
            ... )

            >>> # Connect with path prefix filter
            >>> connection = kili.connections.add(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     prefix="datasets/training/"
            ... )

            >>> # Connect with include/exclude patterns
            >>> connection = kili.connections.add(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     include=["*.jpg", "*.png", "*.jpeg"],
            ...     exclude=["**/temp/*", "**/backup/*"]
            ... )

            >>> # Advanced filtering combination
            >>> connection = kili.connections.add(
            ...     project_id="project_123",
            ...     cloud_storage_integration_id="integration_456",
            ...     prefix="data/images/",
            ...     include=["*.jpg", "*.png"],
            ...     exclude=["*/thumbnails/*"]
            ... )

            >>> # Access connection properties
            >>> connection_id = connection.id
            >>> num_assets = connection.number_of_assets
            >>> project = connection.project_id
        """
        # Validate input parameters
        if not project_id or not project_id.strip():
            raise ValueError("project_id cannot be empty or None")

        if not cloud_storage_integration_id or not cloud_storage_integration_id.strip():
            raise ValueError("cloud_storage_integration_id cannot be empty or None")

        # Access the legacy method directly by calling it from the mixin class
        try:
            result = CloudStorageClientMethods.add_cloud_storage_connection(
                self.client,
                project_id=project_id,
                cloud_storage_integration_id=cloud_storage_integration_id,
                selected_folders=selected_folders,
                prefix=prefix,
                include=include,
                exclude=exclude,
            )
            return ConnectionView(validate_connection(result))
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
    ) -> IdResponse:
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
            An IdResponse object containing the connection ID after synchronization.

        Raises:
            ValueError: If connection_id is invalid or empty.
            RuntimeError: If synchronization fails due to permissions or connectivity issues.
            Exception: If an unexpected error occurs during synchronization.

        Examples:
            >>> # Basic synchronization
            >>> result = kili.connections.sync(connection_id="connection_789")

            >>> # Dry-run to preview changes
            >>> preview = kili.connections.sync(
            ...     connection_id="connection_789",
            ...     dry_run=True
            ... )

            >>> # Full synchronization with cleanup
            >>> result = kili.connections.sync(
            ...     connection_id="connection_789",
            ...     delete_extraneous_files=True,
            ...     dry_run=False
            ... )

            >>> # Access the connection ID
            >>> connection_id = result.id
        """
        # Validate input parameters
        if not connection_id or not connection_id.strip():
            raise ValueError("connection_id cannot be empty or None")

        # Access the legacy method directly by calling it from the mixin class
        try:
            result = CloudStorageClientMethods.synchronize_cloud_storage_connection(
                self.client,
                cloud_storage_connection_id=connection_id,
                delete_extraneous_files=delete_extraneous_files,
                dry_run=dry_run,
            )
            return IdResponse(result)
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
