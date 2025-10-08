"""Label domain contract using TypedDict.

This module provides a TypedDict-based contract for Label entities,
along with validation utilities and helper functions.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from typeguard import check_type

from .user import UserContract

# Label type from domain/label.py
LabelType = Literal["AUTOSAVE", "DEFAULT", "INFERENCE", "PREDICTION", "REVIEW"]


class LabelContract(TypedDict, total=False):
    """TypedDict contract for Label entities.

    This contract represents the core structure of a Label as returned
    from the Kili API. All fields are optional to allow partial data.

    Key fields:
        id: Unique identifier for the label
        author: User who created the label
        jsonResponse: The actual label data/annotations
        createdAt: ISO timestamp of creation
        labelType: Type of label (DEFAULT, REVIEW, etc.)
        modelName: Name of model used (for predictions)
        secondsToLabel: Time spent labeling in seconds
        isLatestLabelForUser: Whether this is the user's latest label
        consensusMark: Consensus quality score
        honeypotMark: Honeypot quality score
        inferenceMark: Inference quality score
    """

    id: str
    author: UserContract
    jsonResponse: Dict[str, Any]
    createdAt: str
    updatedAt: str
    labelType: LabelType
    modelName: Optional[str]
    secondsToLabel: Optional[int]
    isLatestLabelForUser: bool
    isLatestDefaultLabelForUser: bool
    consensusMark: Optional[float]
    honeypotMark: Optional[float]
    inferenceMark: Optional[float]
    skipped: bool
    totalSecondsToLabel: Optional[int]
    numberOfAnnotations: Optional[int]


def validate_label(data: Dict[str, Any]) -> LabelContract:
    """Validate and return a label contract.

    Args:
        data: Dictionary to validate as a LabelContract

    Returns:
        The validated data as a LabelContract

    Raises:
        TypeError: If the data does not match the LabelContract structure
    """
    check_type(data, LabelContract)
    return data  # type: ignore[return-value]


@dataclass(frozen=True)
class LabelView:
    """Read-only view wrapper for LabelContract.

    This dataclass provides ergonomic property access to label data
    while maintaining the underlying dictionary representation.

    Example:
        >>> label_data = {"id": "456", "author": {"email": "user@example.com"}, ...}
        >>> view = LabelView(label_data)
        >>> print(view.id)
        '456'
        >>> print(view.author_email)
        'user@example.com'
    """

    __slots__ = ("_data",)

    _data: LabelContract

    @property
    def id(self) -> str:
        """Get label ID."""
        return self._data.get("id", "")

    @property
    def author(self) -> Optional[UserContract]:
        """Get label author."""
        return self._data.get("author")

    @property
    def author_email(self) -> str:
        """Get author email."""
        author = self.author
        return author.get("email", "") if author else ""

    @property
    def author_id(self) -> str:
        """Get author ID."""
        author = self.author
        return author.get("id", "") if author else ""

    @property
    def json_response(self) -> Dict[str, Any]:
        """Get JSON response (annotation data)."""
        return self._data.get("jsonResponse", {})

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._data.get("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        """Get update timestamp."""
        return self._data.get("updatedAt")

    @property
    def label_type(self) -> Optional[LabelType]:
        """Get label type."""
        return self._data.get("labelType")

    @property
    def model_name(self) -> Optional[str]:
        """Get model name (for predictions)."""
        return self._data.get("modelName")

    @property
    def seconds_to_label(self) -> Optional[int]:
        """Get seconds spent labeling."""
        return self._data.get("secondsToLabel")

    @property
    def is_latest(self) -> bool:
        """Check if this is the latest label for the user."""
        return self._data.get("isLatestLabelForUser", False)

    @property
    def consensus_mark(self) -> Optional[float]:
        """Get consensus quality mark."""
        return self._data.get("consensusMark")

    @property
    def honeypot_mark(self) -> Optional[float]:
        """Get honeypot quality mark."""
        return self._data.get("honeypotMark")

    @property
    def is_prediction(self) -> bool:
        """Check if label is a prediction."""
        return self.label_type in ("PREDICTION", "INFERENCE")

    @property
    def is_review(self) -> bool:
        """Check if label is a review."""
        return self.label_type == "REVIEW"

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the label.

        Returns author email if available, otherwise the label ID.
        """
        return self.author_email or self.id

    def to_dict(self) -> LabelContract:
        """Get the underlying dictionary representation."""
        return self._data


def sort_labels_by_created_at(
    labels: List[LabelContract], reverse: bool = False
) -> List[LabelContract]:
    """Sort labels by creation timestamp.

    Args:
        labels: List of label contracts to sort
        reverse: If True, sort in descending order (newest first)

    Returns:
        Sorted list of labels
    """
    return sorted(
        labels,
        key=lambda label: label.get("createdAt", ""),
        reverse=reverse,
    )


def filter_labels_by_type(
    labels: List[LabelContract], label_type: LabelType
) -> List[LabelContract]:
    """Filter labels by type.

    Args:
        labels: List of label contracts to filter
        label_type: Label type to filter by

    Returns:
        Filtered list of labels
    """
    return [label for label in labels if label.get("labelType") == label_type]


@dataclass(frozen=True)
class LabelExportResponse:
    """Response for label export operations.

    This wraps the export metadata returned when exporting labels without
    saving to a file. The structure contains export information about
    the processed data.

    Example:
        >>> export_result = kili.labels.export(project_id="proj_123", filename=None, fmt="kili")
        >>> if export_result:
        ...     for item in export_result.export_info:
        ...         print(item)
    """

    __slots__ = ("_data",)

    _data: List[Dict[str, Union[List[str], str]]]

    @property
    def export_info(self) -> List[Dict[str, Union[List[str], str]]]:
        """Get export information."""
        return self._data

    def to_list(self) -> List[Dict[str, Union[List[str], str]]]:
        """Get the underlying list representation."""
        return self._data
