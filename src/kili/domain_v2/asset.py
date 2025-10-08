"""Asset domain contract using TypedDict.

This module provides a TypedDict-based contract for Asset entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

from typeguard import check_type

# Asset status types from domain/asset/asset.py
AssetStatus = Literal["TODO", "ONGOING", "LABELED", "REVIEWED", "TO_REVIEW"]
StatusInStep = Literal["TO_DO", "DOING", "PARTIALLY_DONE", "REDO", "DONE", "SKIPPED"]


class CurrentStepContract(TypedDict, total=False):
    """Current workflow step information for an asset."""

    name: str
    status: StatusInStep


class LabelAuthorContract(TypedDict, total=False):
    """Label author information."""

    id: str
    email: str


class AssetLabelContract(TypedDict, total=False):
    """Embedded label information within an asset."""

    id: str
    author: LabelAuthorContract
    createdAt: str
    jsonResponse: Dict[str, Any]


class AssetContract(TypedDict, total=False):
    """TypedDict contract for Asset entities.

    This contract represents the core structure of an Asset as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the asset
        externalId: External reference ID
        content: Asset content (URL or text)
        jsonMetadata: Custom metadata dictionary
        labels: List of labels associated with this asset
        status: Current asset status (workflow v1)
        currentStep: Current workflow step (workflow v2)
        isHoneypot: Whether this is a honeypot asset for quality control
        skipped: Whether the asset has been skipped
        createdAt: ISO timestamp of creation
    """

    id: str
    externalId: str
    content: str
    jsonMetadata: Optional[Dict[str, Any]]
    labels: List[AssetLabelContract]
    latestLabel: AssetLabelContract
    status: AssetStatus
    currentStep: CurrentStepContract
    isHoneypot: bool
    skipped: bool
    createdAt: str
    updatedAt: str
    consensusMark: Optional[float]
    honeypotMark: Optional[float]
    inferenceMark: Optional[float]


def validate_asset(data: Dict[str, Any]) -> AssetContract:
    """Validate and return an asset contract.

    Args:
        data: Dictionary to validate as an AssetContract

    Returns:
        The validated data as an AssetContract

    Raises:
        TypeError: If the data does not match the AssetContract structure
    """
    check_type(data, AssetContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class AssetView:
    """Read-only view wrapper for AssetContract.

    This dataclass provides ergonomic property access to asset data
    while maintaining the underlying dictionary representation.

    Example:
        >>> asset_data = {"id": "123", "externalId": "asset-1", ...}
        >>> view = AssetView(asset_data)
        >>> print(view.id)
        '123'
        >>> print(view.display_name)
        'asset-1'
    """

    __slots__ = ("_data",)

    _data: AssetContract

    @property
    def id(self) -> str:
        """Get asset ID."""
        return self._data.get("id", "")

    @property
    def external_id(self) -> str:
        """Get external ID."""
        return self._data.get("externalId", "")

    @property
    def content(self) -> str:
        """Get asset content."""
        return self._data.get("content", "")

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Get JSON metadata."""
        return self._data.get("jsonMetadata")

    @property
    def labels(self) -> List[AssetLabelContract]:
        """Get list of labels."""
        return self._data.get("labels", [])

    @property
    def latest_label(self) -> Optional[AssetLabelContract]:
        """Get latest label."""
        return self._data.get("latestLabel")

    @property
    def status(self) -> Optional[AssetStatus]:
        """Get asset status (workflow v1)."""
        return self._data.get("status")

    @property
    def current_step(self) -> Optional[CurrentStepContract]:
        """Get current workflow step (workflow v2)."""
        return self._data.get("currentStep")

    @property
    def is_honeypot(self) -> bool:
        """Check if asset is a honeypot."""
        return self._data.get("isHoneypot", False)

    @property
    def skipped(self) -> bool:
        """Check if asset is skipped."""
        return self._data.get("skipped", False)

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the asset.

        Returns the external ID if available, otherwise falls back to the ID.
        """
        return self.external_id or self.id

    @property
    def has_labels(self) -> bool:
        """Check if asset has any labels."""
        return len(self.labels) > 0

    @property
    def label_count(self) -> int:
        """Get the number of labels."""
        return len(self.labels)

    def to_dict(self) -> AssetContract:
        """Get the underlying dictionary representation."""
        return self._data


class WorkflowStepResponseContract(TypedDict, total=False):
    """Response from workflow step operations.

    Contains the project ID and list of affected asset IDs after a workflow
    step operation like invalidating or advancing to the next step.
    """

    id: str
    asset_ids: List[str]


def validate_workflow_step_response(data: Dict[str, Any]) -> WorkflowStepResponseContract:
    """Validate and return a workflow step response contract.

    Args:
        data: Dictionary to validate as a WorkflowStepResponseContract

    Returns:
        The validated data as a WorkflowStepResponseContract

    Raises:
        TypeError: If the data does not match the WorkflowStepResponseContract structure
    """
    check_type(data, WorkflowStepResponseContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class WorkflowStepResponse:
    """Response for workflow step operations.

    Provides typed access to the results of workflow step operations like
    invalidating assets or moving them to the next step.

    Example:
        >>> response = WorkflowStepResponse({"id": "project_123", "asset_ids": ["asset_1", "asset_2"]})
        >>> print(response.id)
        'project_123'
        >>> print(response.asset_ids)
        ['asset_1', 'asset_2']
    """

    __slots__ = ("_data",)

    _data: Union[WorkflowStepResponseContract, Dict[str, Any]]

    @property
    def id(self) -> str:
        """Get the project ID."""
        return str(self._data.get("id", ""))

    @property
    def asset_ids(self) -> List[str]:
        """Get the list of affected asset IDs."""
        return self._data.get("asset_ids", [])

    def to_dict(self) -> WorkflowStepResponseContract:
        """Get the underlying dictionary representation."""
        return cast(WorkflowStepResponseContract, self._data)


class AssetCreateResponseContract(TypedDict, total=False):
    """Response from asset creation operations.

    Contains the project ID and list of created asset IDs.
    """

    id: str
    asset_ids: List[str]


def validate_asset_create_response(data: Dict[str, Any]) -> AssetCreateResponseContract:
    """Validate and return an asset creation response contract.

    Args:
        data: Dictionary to validate as an AssetCreateResponseContract

    Returns:
        The validated data as an AssetCreateResponseContract

    Raises:
        TypeError: If the data does not match the AssetCreateResponseContract structure
    """
    check_type(data, AssetCreateResponseContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class AssetCreateResponse:
    """Response for asset creation with project ID and created asset IDs.

    Example:
        >>> response = AssetCreateResponse({"id": "project_123", "asset_ids": ["asset_1", "asset_2"]})
        >>> print(response.id)
        'project_123'
        >>> print(response.asset_ids)
        ['asset_1', 'asset_2']
    """

    __slots__ = ("_data",)

    _data: Union[AssetCreateResponseContract, Dict[str, Any]]

    @property
    def id(self) -> str:
        """Get the project ID."""
        return str(self._data.get("id", ""))

    @property
    def asset_ids(self) -> List[str]:
        """Get the list of created asset IDs."""
        return self._data.get("asset_ids", [])

    def to_dict(self) -> AssetCreateResponseContract:
        """Get the underlying dictionary representation."""
        return cast(AssetCreateResponseContract, self._data)
