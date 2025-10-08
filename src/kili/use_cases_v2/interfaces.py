"""Repository interface definitions using Protocol for dependency inversion.

This module defines Protocol-based interfaces for repository patterns,
enabling dependency inversion principle in use cases. Use cases depend on
these interfaces rather than concrete implementations.

The interfaces use TypedDict contracts from domain_v2 for type-safe returns.
"""

# pylint: disable=unnecessary-ellipsis,redundant-returns-doc,redundant-yields-doc
# Ellipsis (...) is required for Protocol method definitions
# Docstring returns/yields sections are helpful for interface documentation

from typing import Generator, List, Literal, Optional, Protocol

from kili.domain_v2.asset import AssetContract
from kili.domain_v2.label import LabelContract
from kili.domain_v2.project import ProjectContract
from kili.domain_v2.user import UserContract


class PaginationParams:
    """Pagination parameters for repository queries.

    Attributes:
        skip: Number of items to skip
        first: Maximum number of items to return (None for all)
        batch_size: Size of batches for paginated queries
    """

    def __init__(
        self,
        skip: int = 0,
        first: Optional[int] = None,
        batch_size: int = 100,
    ) -> None:
        """Initialize pagination parameters."""
        self.skip = skip
        self.first = first
        self.batch_size = batch_size


SortOrder = Literal["asc", "desc"]


# Asset Repository Interface


class IAssetRepository(Protocol):
    """Protocol defining the interface for Asset repository operations.

    This interface provides methods for querying and manipulating assets,
    returning validated AssetContract objects.
    """

    def get_by_id(
        self,
        asset_id: str,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[AssetContract]:
        """Get a single asset by ID.

        Args:
            asset_id: The asset ID
            project_id: The project ID containing the asset
            fields: Optional list of fields to retrieve

        Returns:
            AssetContract if found, None otherwise
        """
        ...

    def get_by_external_id(
        self,
        external_id: str,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[AssetContract]:
        """Get a single asset by external ID.

        Args:
            external_id: The external ID
            project_id: The project ID containing the asset
            fields: Optional list of fields to retrieve

        Returns:
            AssetContract if found, None otherwise
        """
        ...

    def list(
        self,
        project_id: str,
        fields: Optional[List[str]] = None,
        status_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
        asset_id_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Generator[AssetContract, None, None]:
        """List assets matching the given filters.

        Args:
            project_id: The project ID
            fields: Optional list of fields to retrieve
            status_in: Filter by asset status
            external_id_in: Filter by external IDs
            asset_id_in: Filter by asset IDs
            metadata_where: Filter by JSON metadata
            created_at_gte: Filter by creation date (greater than or equal)
            created_at_lte: Filter by creation date (less than or equal)
            pagination: Pagination parameters

        Yields:
            AssetContract objects matching the filters
        """
        ...

    def count(
        self,
        project_id: str,
        status_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
    ) -> int:
        """Count assets matching the given filters.

        Args:
            project_id: The project ID
            status_in: Filter by asset status
            external_id_in: Filter by external IDs
            metadata_where: Filter by JSON metadata

        Returns:
            Number of assets matching the filters
        """
        ...

    def create(
        self,
        project_id: str,
        content: str,
        external_id: str,
        json_metadata: Optional[dict] = None,
    ) -> AssetContract:
        """Create a new asset.

        Args:
            project_id: The project ID
            content: Asset content (URL or text)
            external_id: External identifier
            json_metadata: Optional metadata dictionary

        Returns:
            The created AssetContract
        """
        ...

    def update_metadata(
        self,
        asset_id: str,
        json_metadata: dict,
    ) -> AssetContract:
        """Update asset metadata.

        Args:
            asset_id: The asset ID
            json_metadata: New metadata dictionary

        Returns:
            The updated AssetContract
        """
        ...

    def delete(
        self,
        asset_ids: List[str],
    ) -> int:
        """Delete assets by IDs.

        Args:
            asset_ids: List of asset IDs to delete

        Returns:
            Number of assets deleted
        """
        ...


# Label Repository Interface


class ILabelRepository(Protocol):
    """Protocol defining the interface for Label repository operations.

    This interface provides methods for querying and manipulating labels,
    returning validated LabelContract objects.
    """

    def get_by_id(
        self,
        label_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[LabelContract]:
        """Get a single label by ID.

        Args:
            label_id: The label ID
            fields: Optional list of fields to retrieve

        Returns:
            LabelContract if found, None otherwise
        """
        ...

    def list(
        self,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
        fields: Optional[List[str]] = None,
        label_type_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Generator[LabelContract, None, None]:
        """List labels matching the given filters.

        Args:
            asset_id: Filter by asset ID
            project_id: Filter by project ID
            fields: Optional list of fields to retrieve
            label_type_in: Filter by label type
            author_in: Filter by author IDs
            created_at_gte: Filter by creation date (greater than or equal)
            created_at_lte: Filter by creation date (less than or equal)
            pagination: Pagination parameters

        Yields:
            LabelContract objects matching the filters
        """
        ...

    def count(
        self,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
        label_type_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
    ) -> int:
        """Count labels matching the given filters.

        Args:
            asset_id: Filter by asset ID
            project_id: Filter by project ID
            label_type_in: Filter by label type
            author_in: Filter by author IDs

        Returns:
            Number of labels matching the filters
        """
        ...

    def create(
        self,
        asset_id: str,
        json_response: dict,
        label_type: str = "DEFAULT",
        seconds_to_label: Optional[int] = None,
    ) -> LabelContract:
        """Create a new label.

        Args:
            asset_id: The asset ID
            json_response: Label annotation data
            label_type: Type of label (DEFAULT, REVIEW, etc.)
            seconds_to_label: Time spent labeling in seconds

        Returns:
            The created LabelContract
        """
        ...

    def update(
        self,
        label_id: str,
        json_response: dict,
    ) -> LabelContract:
        """Update an existing label.

        Args:
            label_id: The label ID
            json_response: Updated annotation data

        Returns:
            The updated LabelContract
        """
        ...

    def delete(
        self,
        label_ids: List[str],
    ) -> int:
        """Delete labels by IDs.

        Args:
            label_ids: List of label IDs to delete

        Returns:
            Number of labels deleted
        """
        ...


# Project Repository Interface


class IProjectRepository(Protocol):
    """Protocol defining the interface for Project repository operations.

    This interface provides methods for querying and manipulating projects,
    returning validated ProjectContract objects.
    """

    def get_by_id(
        self,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[ProjectContract]:
        """Get a single project by ID.

        Args:
            project_id: The project ID
            fields: Optional list of fields to retrieve

        Returns:
            ProjectContract if found, None otherwise
        """
        ...

    def list(
        self,
        fields: Optional[List[str]] = None,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        input_type_in: Optional[List[str]] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Generator[ProjectContract, None, None]:
        """List projects matching the given filters.

        Args:
            fields: Optional list of fields to retrieve
            archived: Filter by archived status
            starred: Filter by starred status
            input_type_in: Filter by input types (IMAGE, TEXT, etc.)
            created_at_gte: Filter by creation date (greater than or equal)
            created_at_lte: Filter by creation date (less than or equal)
            pagination: Pagination parameters

        Yields:
            ProjectContract objects matching the filters
        """
        ...

    def count(
        self,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        input_type_in: Optional[List[str]] = None,
    ) -> int:
        """Count projects matching the given filters.

        Args:
            archived: Filter by archived status
            starred: Filter by starred status
            input_type_in: Filter by input types

        Returns:
            Number of projects matching the filters
        """
        ...

    def create(
        self,
        title: str,
        description: str,
        input_type: str,
        json_interface: dict,
    ) -> ProjectContract:
        """Create a new project.

        Args:
            title: Project title
            description: Project description
            input_type: Type of input data (IMAGE, TEXT, etc.)
            json_interface: Ontology/interface definition

        Returns:
            The created ProjectContract
        """
        ...

    def update(
        self,
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        json_interface: Optional[dict] = None,
    ) -> ProjectContract:
        """Update an existing project.

        Args:
            project_id: The project ID
            title: Optional new title
            description: Optional new description
            json_interface: Optional new interface definition

        Returns:
            The updated ProjectContract
        """
        ...

    def archive(
        self,
        project_id: str,
    ) -> ProjectContract:
        """Archive a project.

        Args:
            project_id: The project ID

        Returns:
            The archived ProjectContract
        """
        ...

    def delete(
        self,
        project_ids: List[str],
    ) -> int:
        """Delete projects by IDs.

        Args:
            project_ids: List of project IDs to delete

        Returns:
            Number of projects deleted
        """
        ...


# User Repository Interface


class IUserRepository(Protocol):
    """Protocol defining the interface for User repository operations.

    This interface provides methods for querying and manipulating users,
    returning validated UserContract objects.
    """

    def get_by_id(
        self,
        user_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[UserContract]:
        """Get a single user by ID.

        Args:
            user_id: The user ID
            fields: Optional list of fields to retrieve

        Returns:
            UserContract if found, None otherwise
        """
        ...

    def get_by_email(
        self,
        email: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[UserContract]:
        """Get a single user by email.

        Args:
            email: The user email
            fields: Optional list of fields to retrieve

        Returns:
            UserContract if found, None otherwise
        """
        ...

    def list(
        self,
        organization_id: str,
        fields: Optional[List[str]] = None,
        activated: Optional[bool] = None,
        email_contains: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Generator[UserContract, None, None]:
        """List users matching the given filters.

        Args:
            organization_id: The organization ID
            fields: Optional list of fields to retrieve
            activated: Filter by activation status
            email_contains: Filter by email substring
            pagination: Pagination parameters

        Yields:
            UserContract objects matching the filters
        """
        ...

    def count(
        self,
        organization_id: str,
        activated: Optional[bool] = None,
    ) -> int:
        """Count users matching the given filters.

        Args:
            organization_id: The organization ID
            activated: Filter by activation status

        Returns:
            Number of users matching the filters
        """
        ...

    def create(
        self,
        organization_id: str,
        email: str,
        firstname: str,
        lastname: str,
        role: str = "USER",
    ) -> UserContract:
        """Create a new user.

        Args:
            organization_id: The organization ID
            email: User email address
            firstname: User first name
            lastname: User last name
            role: Organization role (ADMIN, USER, REVIEWER)

        Returns:
            The created UserContract
        """
        ...

    def update(
        self,
        user_id: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        activated: Optional[bool] = None,
    ) -> UserContract:
        """Update an existing user.

        Args:
            user_id: The user ID
            firstname: Optional new first name
            lastname: Optional new last name
            activated: Optional new activation status

        Returns:
            The updated UserContract
        """
        ...
