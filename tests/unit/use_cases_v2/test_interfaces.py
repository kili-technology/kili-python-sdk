"""Tests for repository interface definitions.

This module tests that repository interfaces are properly defined and
that mock implementations can comply with the Protocol contracts.
"""

from typing import Generator, List, Optional

from kili.domain_v2.asset import AssetContract
from kili.domain_v2.label import LabelContract
from kili.domain_v2.project import ProjectContract
from kili.domain_v2.user import UserContract
from kili.use_cases_v2.interfaces import (
    IAssetRepository,
    ILabelRepository,
    IProjectRepository,
    IUserRepository,
    PaginationParams,
)

# Mock Asset Repository Implementation


class MockAssetRepository:
    """Mock implementation of IAssetRepository for testing."""

    def __init__(self):
        """Initialize with empty asset store."""
        self._assets: dict[str, AssetContract] = {}
        self._next_id = 1

    def get_by_id(
        self,
        asset_id: str,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[AssetContract]:
        """Get asset by ID."""
        return self._assets.get(asset_id)

    def get_by_external_id(
        self,
        external_id: str,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[AssetContract]:
        """Get asset by external ID."""
        for asset in self._assets.values():
            if asset.get("externalId") == external_id:
                return asset
        return None

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
        """List assets."""
        for asset in self._assets.values():
            if status_in and asset.get("status") not in status_in:
                continue
            if external_id_in and asset.get("externalId") not in external_id_in:
                continue
            if asset_id_in and asset.get("id") not in asset_id_in:
                continue
            yield asset

    def count(
        self,
        project_id: str,
        status_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
    ) -> int:
        """Count assets."""
        return len(list(self.list(project_id, status_in=status_in)))

    def create(
        self,
        project_id: str,
        content: str,
        external_id: str,
        json_metadata: Optional[dict] = None,
    ) -> AssetContract:
        """Create an asset."""
        asset_id = str(self._next_id)
        self._next_id += 1
        asset: AssetContract = {
            "id": asset_id,
            "externalId": external_id,
            "content": content,
            "jsonMetadata": json_metadata,
            "status": "TODO",
            "labels": [],
            "isHoneypot": False,
            "skipped": False,
            "createdAt": "2024-01-01T00:00:00Z",
        }
        self._assets[asset_id] = asset
        return asset

    def update_metadata(
        self,
        asset_id: str,
        json_metadata: dict,
    ) -> AssetContract:
        """Update asset metadata."""
        asset = self._assets[asset_id]
        asset["jsonMetadata"] = json_metadata
        return asset

    def delete(
        self,
        asset_ids: List[str],
    ) -> int:
        """Delete assets."""
        count = 0
        for asset_id in asset_ids:
            if asset_id in self._assets:
                del self._assets[asset_id]
                count += 1
        return count


# Mock Label Repository Implementation


class MockLabelRepository:
    """Mock implementation of ILabelRepository for testing."""

    def __init__(self):
        """Initialize with empty label store."""
        self._labels: dict[str, LabelContract] = {}
        self._next_id = 1

    def get_by_id(
        self,
        label_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[LabelContract]:
        """Get label by ID."""
        return self._labels.get(label_id)

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
        """List labels."""
        for label in self._labels.values():
            if label_type_in and label.get("labelType") not in label_type_in:
                continue
            if author_in and label.get("author", {}).get("id") not in author_in:
                continue
            yield label

    def count(
        self,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
        label_type_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
    ) -> int:
        """Count labels."""
        return len(list(self.list(label_type_in=label_type_in, author_in=author_in)))

    def create(
        self,
        asset_id: str,
        json_response: dict,
        label_type: str = "DEFAULT",
        seconds_to_label: Optional[int] = None,
    ) -> LabelContract:
        """Create a label."""
        label_id = str(self._next_id)
        self._next_id += 1
        label: LabelContract = {
            "id": label_id,
            "author": {"id": "user1", "email": "user@example.com"},
            "jsonResponse": json_response,
            "createdAt": "2024-01-01T00:00:00Z",
            "labelType": label_type,  # type: ignore
            "isLatestLabelForUser": True,
            "isLatestDefaultLabelForUser": True,
            "skipped": False,
        }
        self._labels[label_id] = label
        return label

    def update(
        self,
        label_id: str,
        json_response: dict,
    ) -> LabelContract:
        """Update a label."""
        label = self._labels[label_id]
        label["jsonResponse"] = json_response
        return label

    def delete(
        self,
        label_ids: List[str],
    ) -> int:
        """Delete labels."""
        count = 0
        for label_id in label_ids:
            if label_id in self._labels:
                del self._labels[label_id]
                count += 1
        return count


# Mock Project Repository Implementation


class MockProjectRepository:
    """Mock implementation of IProjectRepository for testing."""

    def __init__(self):
        """Initialize with empty project store."""
        self._projects: dict[str, ProjectContract] = {}
        self._next_id = 1

    def get_by_id(
        self,
        project_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[ProjectContract]:
        """Get project by ID."""
        return self._projects.get(project_id)

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
        """List projects."""
        for project in self._projects.values():
            if archived is not None and project.get("archived") != archived:
                continue
            if starred is not None and project.get("starred") != starred:
                continue
            if input_type_in and project.get("inputType") not in input_type_in:
                continue
            yield project

    def count(
        self,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        input_type_in: Optional[List[str]] = None,
    ) -> int:
        """Count projects."""
        return len(list(self.list(archived=archived, starred=starred)))

    def create(
        self,
        title: str,
        description: str,
        input_type: str,
        json_interface: dict,
    ) -> ProjectContract:
        """Create a project."""
        project_id = str(self._next_id)
        self._next_id += 1
        project: ProjectContract = {
            "id": project_id,
            "title": title,
            "description": description,
            "inputType": input_type,  # type: ignore
            "jsonInterface": json_interface,
            "workflowVersion": "V2",
            "numberOfAssets": 0,
            "archived": False,
            "starred": False,
            "createdAt": "2024-01-01T00:00:00Z",
            "steps": [],
            "roles": [],
            "complianceTags": [],
            "useHoneypot": False,
            "readPermissionsForAssetsAndLabels": True,
            "shouldRelaunchKpiComputation": False,
        }
        self._projects[project_id] = project
        return project

    def update(
        self,
        project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        json_interface: Optional[dict] = None,
    ) -> ProjectContract:
        """Update a project."""
        project = self._projects[project_id]
        if title is not None:
            project["title"] = title
        if description is not None:
            project["description"] = description
        if json_interface is not None:
            project["jsonInterface"] = json_interface
        return project

    def archive(
        self,
        project_id: str,
    ) -> ProjectContract:
        """Archive a project."""
        project = self._projects[project_id]
        project["archived"] = True
        return project

    def delete(
        self,
        project_ids: List[str],
    ) -> int:
        """Delete projects."""
        count = 0
        for project_id in project_ids:
            if project_id in self._projects:
                del self._projects[project_id]
                count += 1
        return count


# Mock User Repository Implementation


class MockUserRepository:
    """Mock implementation of IUserRepository for testing."""

    def __init__(self):
        """Initialize with empty user store."""
        self._users: dict[str, UserContract] = {}
        self._next_id = 1

    def get_by_id(
        self,
        user_id: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[UserContract]:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_by_email(
        self,
        email: str,
        fields: Optional[List[str]] = None,
    ) -> Optional[UserContract]:
        """Get user by email."""
        for user in self._users.values():
            if user.get("email") == email:
                return user
        return None

    def list(
        self,
        organization_id: str,
        fields: Optional[List[str]] = None,
        activated: Optional[bool] = None,
        email_contains: Optional[str] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Generator[UserContract, None, None]:
        """List users."""
        for user in self._users.values():
            if activated is not None and user.get("activated") != activated:
                continue
            if email_contains and email_contains not in user.get("email", ""):
                continue
            yield user

    def count(
        self,
        organization_id: str,
        activated: Optional[bool] = None,
    ) -> int:
        """Count users."""
        return len(list(self.list(organization_id, activated=activated)))

    def create(
        self,
        organization_id: str,
        email: str,
        firstname: str,
        lastname: str,
        role: str = "USER",
    ) -> UserContract:
        """Create a user."""
        user_id = str(self._next_id)
        self._next_id += 1
        user: UserContract = {
            "id": user_id,
            "email": email,
            "name": f"{firstname} {lastname}",
            "firstname": firstname,
            "lastname": lastname,
            "activated": True,
            "organizationId": organization_id,
            "organizationRole": {"id": "role1", "role": role},  # type: ignore
            "createdAt": "2024-01-01T00:00:00Z",
            "hubspotSubscriptionStatus": "SUBSCRIBED",
            "apiKey": "key123",
        }
        self._users[user_id] = user
        return user

    def update(
        self,
        user_id: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        activated: Optional[bool] = None,
    ) -> UserContract:
        """Update a user."""
        user = self._users[user_id]
        if firstname is not None:
            user["firstname"] = firstname
        if lastname is not None:
            user["lastname"] = lastname
        if activated is not None:
            user["activated"] = activated
        return user


# Protocol Compliance Tests


def test_asset_repository_protocol_compliance():
    """Test that MockAssetRepository complies with IAssetRepository protocol."""
    repo: IAssetRepository = MockAssetRepository()

    # Test create
    asset = repo.create(
        project_id="proj1",
        content="https://example.com/image.jpg",
        external_id="asset-1",
        json_metadata={"key": "value"},
    )
    asset_id = asset.get("id")
    assert asset_id is not None
    assert asset.get("externalId") == "asset-1"
    assert asset.get("content") == "https://example.com/image.jpg"

    # Test get_by_id
    retrieved = repo.get_by_id(asset_id, "proj1")
    assert retrieved is not None
    assert retrieved.get("id") == asset_id

    # Test get_by_external_id
    retrieved_by_ext = repo.get_by_external_id("asset-1", "proj1")
    assert retrieved_by_ext is not None
    assert retrieved_by_ext.get("externalId") == "asset-1"

    # Test list
    assets = list(repo.list("proj1"))
    assert len(assets) == 1

    # Test count
    count = repo.count("proj1")
    assert count == 1

    # Test update_metadata
    updated = repo.update_metadata(asset_id, {"new_key": "new_value"})
    assert updated.get("jsonMetadata") == {"new_key": "new_value"}

    # Test delete
    deleted = repo.delete([asset_id])
    assert deleted == 1
    assert repo.count("proj1") == 0


def test_label_repository_protocol_compliance():
    """Test that MockLabelRepository complies with ILabelRepository protocol."""
    repo: ILabelRepository = MockLabelRepository()

    # Test create
    label = repo.create(
        asset_id="asset1",
        json_response={"annotation": "value"},
        label_type="DEFAULT",
    )
    label_id = label.get("id")
    assert label_id is not None
    assert label.get("jsonResponse") == {"annotation": "value"}

    # Test get_by_id
    retrieved = repo.get_by_id(label_id)
    assert retrieved is not None
    assert retrieved.get("id") == label_id

    # Test list
    labels = list(repo.list())
    assert len(labels) == 1

    # Test count
    count = repo.count()
    assert count == 1

    # Test update
    updated = repo.update(label_id, {"updated": "annotation"})
    assert updated.get("jsonResponse") == {"updated": "annotation"}

    # Test delete
    deleted = repo.delete([label_id])
    assert deleted == 1
    assert repo.count() == 0


def test_project_repository_protocol_compliance():
    """Test that MockProjectRepository complies with IProjectRepository protocol."""
    repo: IProjectRepository = MockProjectRepository()

    # Test create
    project = repo.create(
        title="Test Project",
        description="A test project",
        input_type="IMAGE",
        json_interface={"jobs": []},
    )
    project_id = project.get("id")
    assert project_id is not None
    assert project.get("title") == "Test Project"

    # Test get_by_id
    retrieved = repo.get_by_id(project_id)
    assert retrieved is not None
    assert retrieved.get("id") == project_id

    # Test list
    projects = list(repo.list())
    assert len(projects) == 1

    # Test count
    count = repo.count()
    assert count == 1

    # Test update
    updated = repo.update(project_id, title="Updated Title")
    assert updated.get("title") == "Updated Title"

    # Test archive
    archived = repo.archive(project_id)
    assert archived.get("archived") is True

    # Test delete
    deleted = repo.delete([project_id])
    assert deleted == 1
    assert repo.count(archived=True) == 0


def test_user_repository_protocol_compliance():
    """Test that MockUserRepository complies with IUserRepository protocol."""
    repo: IUserRepository = MockUserRepository()

    # Test create
    user = repo.create(
        organization_id="org1",
        email="test@example.com",
        firstname="John",
        lastname="Doe",
        role="USER",
    )
    user_id = user.get("id")
    assert user_id is not None
    assert user.get("email") == "test@example.com"

    # Test get_by_id
    retrieved = repo.get_by_id(user_id)
    assert retrieved is not None
    assert retrieved.get("id") == user_id

    # Test get_by_email
    retrieved_by_email = repo.get_by_email("test@example.com")
    assert retrieved_by_email is not None
    assert retrieved_by_email.get("email") == "test@example.com"

    # Test list
    users = list(repo.list("org1"))
    assert len(users) == 1

    # Test count
    count = repo.count("org1")
    assert count == 1

    # Test update
    updated = repo.update(user_id, firstname="Jane")
    assert updated.get("firstname") == "Jane"


def test_pagination_params():
    """Test PaginationParams initialization."""
    # Default params
    params = PaginationParams()
    assert params.skip == 0
    assert params.first is None
    assert params.batch_size == 100

    # Custom params
    params = PaginationParams(skip=10, first=50, batch_size=25)
    assert params.skip == 10
    assert params.first == 50
    assert params.batch_size == 25


def test_asset_repository_filtering():
    """Test asset repository filtering functionality."""
    repo: IAssetRepository = MockAssetRepository()

    # Create multiple assets with different statuses
    asset1 = repo.create("proj1", "content1", "asset-1", {"key": "value1"})
    asset2 = repo.create("proj1", "content2", "asset-2", {"key": "value2"})
    asset3 = repo.create("proj1", "content3", "asset-3", {"key": "value3"})

    # Manually set status to test filtering (since create sets all to TODO)
    asset2_id = asset2.get("id")
    assert asset2_id is not None
    repo._assets[asset2_id]["status"] = "LABELED"

    # Filter by status
    todo_assets = list(repo.list("proj1", status_in=["TODO"]))
    assert len(todo_assets) == 2

    # Filter by external_id
    filtered = list(repo.list("proj1", external_id_in=["asset-1", "asset-2"]))
    assert len(filtered) == 2


def test_label_repository_filtering():
    """Test label repository filtering functionality."""
    repo: ILabelRepository = MockLabelRepository()

    # Create multiple labels with different types
    repo.create("asset1", {"data": 1}, "DEFAULT")
    repo.create("asset1", {"data": 2}, "REVIEW")
    repo.create("asset2", {"data": 3}, "DEFAULT")

    # Filter by label type
    default_labels = list(repo.list(label_type_in=["DEFAULT"]))
    assert len(default_labels) == 2

    review_labels = list(repo.list(label_type_in=["REVIEW"]))
    assert len(review_labels) == 1


def test_project_repository_filtering():
    """Test project repository filtering functionality."""
    repo: IProjectRepository = MockProjectRepository()

    # Create multiple projects
    proj1 = repo.create("Project 1", "Desc 1", "IMAGE", {})
    repo.create("Project 2", "Desc 2", "TEXT", {})
    proj1_id = proj1.get("id")
    assert proj1_id is not None
    repo.archive(proj1_id)

    # Filter by archived status
    archived_projects = list(repo.list(archived=True))
    assert len(archived_projects) == 1

    active_projects = list(repo.list(archived=False))
    assert len(active_projects) == 1

    # Filter by input type
    image_projects = list(repo.list(input_type_in=["IMAGE"]))
    assert len(image_projects) == 1


def test_user_repository_filtering():
    """Test user repository filtering functionality."""
    repo: IUserRepository = MockUserRepository()

    # Create multiple users
    user1 = repo.create("org1", "alice@example.com", "Alice", "Smith")
    repo.create("org1", "bob@example.com", "Bob", "Jones")
    user1_id = user1.get("id")
    assert user1_id is not None
    repo.update(user1_id, activated=False)

    # Filter by activated status
    active_users = list(repo.list("org1", activated=True))
    assert len(active_users) == 1

    inactive_users = list(repo.list("org1", activated=False))
    assert len(inactive_users) == 1

    # Filter by email substring
    alice_users = list(repo.list("org1", email_contains="alice"))
    assert len(alice_users) == 1


def test_repository_returns_correct_types():
    """Test that repositories return correct TypedDict types."""
    asset_repo: IAssetRepository = MockAssetRepository()
    label_repo: ILabelRepository = MockLabelRepository()
    project_repo: IProjectRepository = MockProjectRepository()
    user_repo: IUserRepository = MockUserRepository()

    # Create entities
    asset = asset_repo.create("proj1", "content", "ext-1")
    label = label_repo.create("asset1", {"data": "test"})
    project = project_repo.create("Title", "Desc", "IMAGE", {})
    user = user_repo.create("org1", "user@example.com", "First", "Last")

    # Verify types
    assert isinstance(asset, dict)
    assert isinstance(label, dict)
    assert isinstance(project, dict)
    assert isinstance(user, dict)

    # Verify required fields
    assert "id" in asset
    assert "externalId" in asset
    assert "id" in label
    assert "jsonResponse" in label
    assert "id" in project
    assert "title" in project
    assert "id" in user
    assert "email" in user
