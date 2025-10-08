"""Request/response recording for equivalence testing.

This module provides the ability to record API requests and responses
from legacy client methods for later replay against v2 implementations.
"""

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class RecordedRequest:
    """A recorded API request with its response.

    This class captures all information needed to replay a request
    against a different implementation.
    """

    # Request metadata
    timestamp: str
    method_name: str
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)

    # Response data
    response: Any = None
    exception: Optional[str] = None
    exception_type: Optional[str] = None

    # Context
    project_id: Optional[str] = None
    asset_id: Optional[str] = None
    label_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "method_name": self.method_name,
            "args": self.args,
            "kwargs": self.kwargs,
            "response": self.response,
            "exception": self.exception,
            "exception_type": self.exception_type,
            "project_id": self.project_id,
            "asset_id": self.asset_id,
            "label_id": self.label_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecordedRequest":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            method_name=data["method_name"],
            args=tuple(data.get("args", ())),
            kwargs=data.get("kwargs", {}),
            response=data.get("response"),
            exception=data.get("exception"),
            exception_type=data.get("exception_type"),
            project_id=data.get("project_id"),
            asset_id=data.get("asset_id"),
            label_id=data.get("label_id"),
        )


class RequestRecorder:
    """Records API requests and responses for later replay.

    This class provides functionality to record method calls, responses,
    and exceptions from legacy client implementations.
    """

    def __init__(self, storage_dir: Optional[Union[str, Path]] = None):
        """Initialize the recorder.

        Args:
            storage_dir: Directory to store recordings (default: ./recordings)
        """
        self.storage_dir = Path(storage_dir or "./recordings")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.recordings: List[RecordedRequest] = []

    def record(
        self,
        method_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        response: Any = None,
        exception: Optional[Exception] = None,
        context: Optional[Dict[str, str]] = None,
    ) -> RecordedRequest:
        """Record a method call and its response.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            response: Response from the method
            exception: Exception raised (if any)
            context: Additional context (project_id, asset_id, etc.)

        Returns:
            The recorded request object
        """
        kwargs = kwargs or {}
        context = context or {}

        # Serialize exception if present
        exception_str = None
        exception_type = None
        if exception:
            exception_str = str(exception)
            exception_type = type(exception).__name__

        recording = RecordedRequest(
            timestamp=datetime.utcnow().isoformat(),
            method_name=method_name,
            args=args,
            kwargs=kwargs,
            response=response,
            exception=exception_str,
            exception_type=exception_type,
            project_id=context.get("project_id"),
            asset_id=context.get("asset_id"),
            label_id=context.get("label_id"),
        )

        self.recordings.append(recording)
        return recording

    def save(self, filename: str, format: str = "json") -> Path:
        """Save recordings to file.

        Args:
            filename: Name of the file (without extension)
            format: Format to save ('json' or 'pickle')

        Returns:
            Path to the saved file
        """
        if format == "json":
            filepath = self.storage_dir / f"{filename}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    [r.to_dict() for r in self.recordings],
                    f,
                    indent=2,
                    default=str,  # Handle non-serializable types
                )
        elif format == "pickle":
            filepath = self.storage_dir / f"{filename}.pkl"
            with open(filepath, "wb") as f:
                pickle.dump(self.recordings, f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def load(self, filepath: Union[str, Path]) -> List[RecordedRequest]:
        """Load recordings from file.

        Args:
            filepath: Path to the recordings file

        Returns:
            List of recorded requests
        """
        filepath = Path(filepath)

        if filepath.suffix == ".json":
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
                self.recordings = [RecordedRequest.from_dict(r) for r in data]
        elif filepath.suffix == ".pkl":
            with open(filepath, "rb") as f:
                self.recordings = pickle.load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

        return self.recordings

    def clear(self) -> None:
        """Clear all recordings."""
        self.recordings.clear()

    def filter_by_method(self, method_name: str) -> List[RecordedRequest]:
        """Filter recordings by method name.

        Args:
            method_name: Name of the method to filter by

        Returns:
            List of recordings matching the method name
        """
        return [r for r in self.recordings if r.method_name == method_name]

    def filter_by_context(
        self,
        project_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        label_id: Optional[str] = None,
    ) -> List[RecordedRequest]:
        """Filter recordings by context.

        Args:
            project_id: Filter by project ID
            asset_id: Filter by asset ID
            label_id: Filter by label ID

        Returns:
            List of recordings matching the context
        """
        filtered = self.recordings

        if project_id is not None:
            filtered = [r for r in filtered if r.project_id == project_id]

        if asset_id is not None:
            filtered = [r for r in filtered if r.asset_id == asset_id]

        if label_id is not None:
            filtered = [r for r in filtered if r.label_id == label_id]

        return filtered

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of recorded requests.

        Returns:
            Dictionary with summary statistics
        """
        methods = {}
        for recording in self.recordings:
            method = recording.method_name
            if method not in methods:
                methods[method] = {
                    "count": 0,
                    "success": 0,
                    "errors": 0,
                }
            methods[method]["count"] += 1
            if recording.exception:
                methods[method]["errors"] += 1
            else:
                methods[method]["success"] += 1

        return {
            "total_recordings": len(self.recordings),
            "methods": methods,
            "time_range": {
                "start": min((r.timestamp for r in self.recordings), default=None),
                "end": max((r.timestamp for r in self.recordings), default=None),
            },
        }
