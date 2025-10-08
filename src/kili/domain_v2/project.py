"""Project domain contract using TypedDict.

This module provides a TypedDict-based contract for Project entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

from typeguard import check_type

# Types from domain/project.py
InputType = Literal[
    "IMAGE", "GEOSPATIAL", "PDF", "TEXT", "VIDEO", "LLM_RLHF", "LLM_INSTR_FOLLOWING", "LLM_STATIC"
]
WorkflowVersion = Literal["V1", "V2"]
ComplianceTag = Literal["PHI", "PII"]


class ProjectStepContract(TypedDict, total=False):
    """Project workflow step information."""

    id: str
    name: str
    type: Literal["DEFAULT", "REVIEW"]
    order: int
    stepCoverage: Optional[int]
    consensusCoverage: Optional[int]
    numberOfExpectedLabelsForConsensus: Optional[int]


class ProjectRoleContract(TypedDict, total=False):
    """Project role information."""

    id: str
    role: Literal["ADMIN", "TEAM_MANAGER", "LABELER", "REVIEWER"]
    user: Dict[str, Any]


class ProjectContract(TypedDict, total=False):
    """TypedDict contract for Project entities.

    This contract represents the core structure of a Project as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the project
        title: Project title/name
        description: Project description
        inputType: Type of input data (IMAGE, TEXT, etc.)
        jsonInterface: Ontology/interface definition
        workflowVersion: Workflow version (V1 or V2)
        steps: Workflow steps (for V2 projects)
        roles: User roles in the project
        numberOfAssets: Total number of assets
        createdAt: ISO timestamp of creation
        archived: Whether project is archived
    """

    id: str
    title: str
    description: str
    inputType: InputType
    jsonInterface: Dict[str, Any]
    workflowVersion: WorkflowVersion
    steps: List[ProjectStepContract]
    roles: List[ProjectRoleContract]
    numberOfAssets: int
    numberOfSkippedAssets: int
    numberOfRemainingAssets: int
    numberOfReviewedAssets: int
    numberOfLatestLabels: int
    createdAt: str
    updatedAt: str
    archived: bool
    starred: bool
    complianceTags: List[ComplianceTag]
    consensusTotCoverage: Optional[int]
    minConsensusSize: Optional[int]
    useHoneypot: bool
    consensusMark: Optional[float]
    honeypotMark: Optional[float]
    reviewCoverage: Optional[int]
    shouldRelaunchKpiComputation: bool
    readPermissionsForAssetsAndLabels: bool


def validate_project(data: Dict[str, Any]) -> ProjectContract:
    """Validate and return a project contract.

    Args:
        data: Dictionary to validate as a ProjectContract

    Returns:
        The validated data as a ProjectContract

    Raises:
        TypeError: If the data does not match the ProjectContract structure
    """
    check_type(data, ProjectContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class ProjectView:
    """Read-only view wrapper for ProjectContract.

    This dataclass provides ergonomic property access to project data
    while maintaining the underlying dictionary representation.

    Example:
        >>> project_data = {"id": "789", "title": "My Project", ...}
        >>> view = ProjectView(project_data)
        >>> print(view.id)
        '789'
        >>> print(view.display_name)
        'My Project'
    """

    __slots__ = ("_data",)

    _data: ProjectContract

    @property
    def id(self) -> str:
        """Get project ID."""
        return self._data.get("id", "")

    @property
    def title(self) -> str:
        """Get project title."""
        return self._data.get("title", "")

    @property
    def description(self) -> str:
        """Get project description."""
        return self._data.get("description", "")

    @property
    def input_type(self) -> Optional[InputType]:
        """Get input type."""
        return self._data.get("inputType")

    @property
    def json_interface(self) -> Dict[str, Any]:
        """Get JSON interface (ontology)."""
        return self._data.get("jsonInterface", {})

    @property
    def workflow_version(self) -> Optional[WorkflowVersion]:
        """Get workflow version."""
        return self._data.get("workflowVersion")

    @property
    def steps(self) -> List[ProjectStepContract]:
        """Get workflow steps."""
        return self._data.get("steps", [])

    @property
    def roles(self) -> List[ProjectRoleContract]:
        """Get project roles."""
        return self._data.get("roles", [])

    @property
    def number_of_assets(self) -> int:
        """Get total number of assets."""
        return self._data.get("numberOfAssets", 0)

    @property
    def number_of_remaining_assets(self) -> int:
        """Get number of remaining assets."""
        return self._data.get("numberOfRemainingAssets", 0)

    @property
    def number_of_reviewed_assets(self) -> int:
        """Get number of reviewed assets."""
        return self._data.get("numberOfReviewedAssets", 0)

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        """Get update timestamp."""
        return self._data.get("updatedAt")

    @property
    def archived(self) -> bool:
        """Check if project is archived."""
        return self._data.get("archived", False)

    @property
    def starred(self) -> bool:
        """Check if project is starred."""
        return self._data.get("starred", False)

    @property
    def is_v2_workflow(self) -> bool:
        """Check if project uses workflow V2."""
        return self.workflow_version == "V2"

    @property
    def has_honeypot(self) -> bool:
        """Check if project uses honeypot assets."""
        return self._data.get("useHoneypot", False)

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the project.

        Returns the title.
        """
        return self.title or self.id

    @property
    def progress_percentage(self) -> float:
        """Calculate project completion percentage.

        Returns:
            Percentage of completed assets (0-100)
        """
        total = self.number_of_assets
        if total == 0:
            return 0.0
        remaining = self.number_of_remaining_assets
        completed = total - remaining
        return (completed / total) * 100

    def to_dict(self) -> ProjectContract:
        """Get the underlying dictionary representation."""
        return self._data


def get_step_by_name(project: ProjectContract, step_name: str) -> Optional[ProjectStepContract]:
    """Get a workflow step by name.

    Args:
        project: Project contract
        step_name: Name of the step to find

    Returns:
        Step contract if found, None otherwise
    """
    steps = project.get("steps", [])
    for step in steps:
        if step.get("name") == step_name:
            return step
    return None


def get_ordered_steps(project: ProjectContract) -> List[ProjectStepContract]:
    """Get workflow steps ordered by their order field.

    Args:
        project: Project contract

    Returns:
        List of steps sorted by order
    """
    steps = project.get("steps", [])
    return sorted(steps, key=lambda s: s.get("order", 0))


class ProjectVersionContract(TypedDict, total=False):
    """TypedDict contract for ProjectVersion entities.

    This contract represents the structure of a project version
    as returned from the Kili API.

    Key fields:
        id: Unique identifier for the version
        name: Version name
        content: Link to download the version
        createdAt: ISO timestamp of creation
        projectId: ID of the associated project
    """

    id: str
    name: str
    content: Optional[str]
    createdAt: str
    projectId: str


def validate_project_version(data: Dict[str, Any]) -> ProjectVersionContract:
    """Validate and return a project version contract.

    Args:
        data: Dictionary to validate as a ProjectVersionContract

    Returns:
        The validated data as a ProjectVersionContract

    Raises:
        TypeError: If the data does not match the ProjectVersionContract structure
    """
    check_type(data, ProjectVersionContract)
    return data  # type: ignore[return-value]


def validate_project_role(data: Dict[str, Any]) -> ProjectRoleContract:
    """Validate and return a project role contract.

    Args:
        data: Dictionary to validate as a ProjectRoleContract

    Returns:
        The validated data as a ProjectRoleContract

    Raises:
        TypeError: If the data does not match the ProjectRoleContract structure
    """
    check_type(data, ProjectRoleContract)
    return data  # type: ignore[return-value]


def validate_workflow_step(data: Dict[str, Any]) -> ProjectStepContract:
    """Validate and return a workflow step contract.

    Args:
        data: Dictionary to validate as a ProjectStepContract

    Returns:
        The validated data as a ProjectStepContract

    Raises:
        TypeError: If the data does not match the ProjectStepContract structure
    """
    check_type(data, ProjectStepContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class IdResponse:
    """Simple response containing only an ID.

    This is used for mutation operations that return just an ID,
    providing a typed alternative to Dict[Literal["id"], str].

    Example:
        >>> response = IdResponse({"id": "project_123"})
        >>> print(response.id)
        'project_123'
    """

    __slots__ = ("_data",)

    _data: Union[Dict[Literal["id"], str], Dict[str, Any]]

    @property
    def id(self) -> str:
        """Get the ID."""
        return str(self._data.get("id", ""))

    def to_dict(self) -> Dict[str, Any]:
        """Get the underlying dictionary representation."""
        return cast(Dict[str, Any], self._data)


@dataclass(frozen=True)
class IdListResponse:
    """Response containing a list of IDs.

    This is used for mutation operations that return multiple IDs,
    providing a typed alternative to List[Dict[Literal["id"], str]].

    Example:
        >>> response = IdListResponse([{"id": "item_1"}, {"id": "item_2"}])
        >>> print(response.ids)
        ['item_1', 'item_2']
    """

    __slots__ = ("_data",)

    _data: Union[List[Dict[Literal["id"], str]], List[Dict[str, Any]]]

    @property
    def ids(self) -> List[str]:
        """Get the list of IDs."""
        return [str(item.get("id", "")) for item in self._data]

    def to_list(self) -> List[Dict[str, Any]]:
        """Get the underlying list representation."""
        return cast(List[Dict[str, Any]], self._data)


@dataclass(frozen=True)
class StatusResponse:
    """Response containing operation status and result.

    This is used for operations that return status information about an action.

    Example:
        >>> response = StatusResponse({"id": "item_1", "status": "SOLVED", "success": True})
        >>> print(response.success)
        True
    """

    __slots__ = ("_data",)

    _data: Dict[str, Any]

    @property
    def id(self) -> str:
        """Get the ID of the affected item."""
        return str(self._data.get("id", ""))

    @property
    def success(self) -> bool:
        """Check if the operation was successful."""
        return bool(self._data.get("success", False))

    @property
    def status(self) -> Optional[str]:
        """Get the status value if present."""
        return self._data.get("status")

    @property
    def error(self) -> Optional[str]:
        """Get the error message if operation failed."""
        return self._data.get("error")

    def to_dict(self) -> Dict[str, Any]:
        """Get the underlying dictionary representation."""
        return self._data


@dataclass(frozen=True)
class ProjectRoleView:
    """Read-only view wrapper for ProjectRoleContract.

    This dataclass provides ergonomic property access to project role data.

    Example:
        >>> role_data = {"id": "role_1", "role": "ADMIN", "user": {"id": "user_1", "email": "admin@example.com"}}
        >>> view = ProjectRoleView(role_data)
        >>> print(view.role)
        'ADMIN'
        >>> print(view.user_email)
        'admin@example.com'
    """

    __slots__ = ("_data",)

    _data: ProjectRoleContract

    @property
    def id(self) -> str:
        """Get role ID."""
        return self._data.get("id", "")

    @property
    def role(self) -> Optional[Literal["ADMIN", "TEAM_MANAGER", "LABELER", "REVIEWER"]]:
        """Get the role type."""
        return self._data.get("role")

    @property
    def user(self) -> Dict[str, Any]:
        """Get user information."""
        return self._data.get("user", {})

    @property
    def user_id(self) -> str:
        """Get user ID from nested user object."""
        return self.user.get("id", "")

    @property
    def user_email(self) -> str:
        """Get user email from nested user object."""
        return self.user.get("email", "")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name."""
        return f"{self.user_email} ({self.role})" if self.user_email else self.id

    def to_dict(self) -> ProjectRoleContract:
        """Get the underlying dictionary representation."""
        return self._data


@dataclass(frozen=True)
class WorkflowStepView:
    """Read-only view wrapper for ProjectStepContract.

    This dataclass provides ergonomic property access to workflow step data.

    Example:
        >>> step_data = {"id": "step_1", "name": "Labeling", "type": "DEFAULT", "order": 1}
        >>> view = WorkflowStepView(step_data)
        >>> print(view.name)
        'Labeling'
        >>> print(view.is_review_step)
        False
    """

    __slots__ = ("_data",)

    _data: ProjectStepContract

    @property
    def id(self) -> str:
        """Get step ID."""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """Get step name."""
        return self._data.get("name", "")

    @property
    def type(self) -> Optional[Literal["DEFAULT", "REVIEW"]]:
        """Get step type."""
        return self._data.get("type")

    @property
    def order(self) -> int:
        """Get step order."""
        return self._data.get("order", 0)

    @property
    def step_coverage(self) -> Optional[int]:
        """Get step coverage percentage."""
        return self._data.get("stepCoverage")

    @property
    def consensus_coverage(self) -> Optional[int]:
        """Get consensus coverage."""
        return self._data.get("consensusCoverage")

    @property
    def number_of_expected_labels_for_consensus(self) -> Optional[int]:
        """Get expected number of labels for consensus."""
        return self._data.get("numberOfExpectedLabelsForConsensus")

    @property
    def is_review_step(self) -> bool:
        """Check if this is a review step."""
        return self.type == "REVIEW"

    @property
    def display_name(self) -> str:
        """Get a human-readable display name."""
        return self.name or self.id

    def to_dict(self) -> ProjectStepContract:
        """Get the underlying dictionary representation."""
        return self._data


@dataclass(frozen=True)
class ProjectVersionView:
    """Read-only view wrapper for ProjectVersionContract.

    This dataclass provides ergonomic property access to project version data.

    Example:
        >>> version_data = {"id": "v1", "name": "Version 1.0", "projectId": "proj_1"}
        >>> view = ProjectVersionView(version_data)
        >>> print(view.name)
        'Version 1.0'
    """

    __slots__ = ("_data",)

    _data: ProjectVersionContract

    @property
    def id(self) -> str:
        """Get version ID."""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """Get version name."""
        return self._data.get("name", "")

    @property
    def content(self) -> Optional[str]:
        """Get version content/download link."""
        return self._data.get("content")

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def project_id(self) -> str:
        """Get associated project ID."""
        return self._data.get("projectId", "")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name."""
        return self.name or self.id

    def to_dict(self) -> ProjectVersionContract:
        """Get the underlying dictionary representation."""
        return self._data
