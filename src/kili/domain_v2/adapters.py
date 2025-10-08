"""DataFrame adapter utilities for domain contracts.

This module provides utilities to convert between domain contracts and
pandas DataFrames without mutating the original payloads.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union

try:
    import pandas as pd

    PANDAS_AVAILABLE: bool = True
except ImportError:
    PANDAS_AVAILABLE = False
    if not TYPE_CHECKING:
        pd = None  # type: ignore[assignment]

from .asset import AssetContract, AssetView, validate_asset
from .label import LabelContract, LabelView, validate_label
from .project import ProjectContract, ProjectView, validate_project
from .user import UserContract, UserView, validate_user

T = TypeVar("T", AssetContract, LabelContract, ProjectContract, UserContract)
V = TypeVar("V", AssetView, LabelView, ProjectView, UserView)


class DataFrameAdapter:
    """Adapter for converting domain contracts to/from DataFrames.

    This adapter provides methods to convert validated domain contracts
    into pandas DataFrames and vice versa, without mutating the original data.

    Example:
        >>> assets = [{"id": "1", "externalId": "asset-1"}, ...]
        >>> adapter = DataFrameAdapter()
        >>> df = adapter.to_dataframe(assets, AssetContract)
        >>> contracts = adapter.from_dataframe(df, AssetContract)
    """

    def __init__(self) -> None:
        """Initialize the DataFrame adapter."""
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas is required for DataFrame adapters. Install it with: pip install pandas"
            )

    @staticmethod
    def to_dataframe(
        contracts: List[T],
        contract_type: Optional[Type[T]] = None,
        validate: bool = True,
    ) -> "pd.DataFrame":
        """Convert a list of domain contracts to a DataFrame.

        Args:
            contracts: List of domain contracts
            contract_type: Type of contract for validation (optional)
            validate: If True, validate each contract before conversion

        Returns:
            pandas DataFrame with contract data

        Raises:
            TypeError: If validation fails
            ImportError: If pandas is not available
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame conversion")

        if not contracts:
            if not PANDAS_AVAILABLE:
                raise ImportError("pandas is required")
            assert pd is not None  # For type checker
            return pd.DataFrame()

        # Validate contracts if requested
        if validate and contract_type:
            validators = {
                AssetContract: validate_asset,
                LabelContract: validate_label,
                ProjectContract: validate_project,
                UserContract: validate_user,
            }
            validator = validators.get(contract_type)
            if validator:
                contracts = [validator(c) for c in contracts]  # type: ignore

        # Create DataFrame from contracts
        # This creates a copy, not mutating original data
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required")
        assert pd is not None  # For type checker
        return pd.DataFrame(contracts)

    @staticmethod
    def from_dataframe(
        df: "pd.DataFrame",
        contract_type: Type[T],
        validate: bool = True,
    ) -> List[T]:
        """Convert a DataFrame to a list of domain contracts.

        Args:
            df: pandas DataFrame
            contract_type: Type of contract to convert to
            validate: If True, validate each contract after conversion

        Returns:
            List of domain contracts

        Raises:
            TypeError: If validation fails
            ImportError: If pandas is not available
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for DataFrame conversion")

        # Convert DataFrame to list of dictionaries
        contracts = df.to_dict("records")

        # Validate contracts if requested
        if validate:
            validators = {
                AssetContract: validate_asset,
                LabelContract: validate_label,
                ProjectContract: validate_project,
                UserContract: validate_user,
            }
            validator = validators.get(contract_type)
            if validator:
                contracts = [validator(c) for c in contracts]  # type: ignore

        return contracts  # type: ignore

    @staticmethod
    def wrap_contracts(
        contracts: List[T],
        view_type: Type[V],
    ) -> List[V]:
        """Wrap a list of contracts in view wrappers.

        Args:
            contracts: List of domain contracts
            view_type: Type of view wrapper

        Returns:
            List of view wrappers

        Example:
            >>> assets = [{"id": "1", ...}, {"id": "2", ...}]
            >>> views = DataFrameAdapter.wrap_contracts(assets, AssetView)
            >>> print(views[0].display_name)
        """
        return [view_type(contract) for contract in contracts]  # type: ignore

    @staticmethod
    def unwrap_views(views: List[V]) -> List[Dict[str, Any]]:
        """Unwrap view wrappers back to dictionaries.

        Args:
            views: List of view wrappers

        Returns:
            List of dictionaries
        """
        return [view.to_dict() for view in views]  # type: ignore[misc]


class ContractValidator:
    """Validator for domain contracts.

    This class provides validation utilities for domain contracts,
    including batch validation and error reporting.
    """

    @staticmethod
    def validate_batch(
        contracts: List[Dict[str, Any]],
        contract_type: Type[T],
    ) -> tuple[List[T], List[tuple[int, Exception]]]:
        """Validate a batch of contracts and collect errors.

        Args:
            contracts: List of dictionaries to validate
            contract_type: Type of contract to validate against

        Returns:
            Tuple of (valid_contracts, errors)
            where errors is a list of (index, exception) tuples
        """
        validators = {
            AssetContract: validate_asset,
            LabelContract: validate_label,
            ProjectContract: validate_project,
            UserContract: validate_user,
        }

        validator = validators.get(contract_type)
        if not validator:
            raise ValueError(f"Unknown contract type: {contract_type}")

        valid_contracts: List[T] = []
        errors: List[tuple[int, Exception]] = []

        for i, contract in enumerate(contracts):
            try:
                validated = validator(contract)  # type: ignore
                valid_contracts.append(validated)  # type: ignore
            except Exception as e:  # pylint: disable=broad-except
                errors.append((i, e))

        return valid_contracts, errors

    @staticmethod
    def validate_single(
        contract: Dict[str, Any],
        contract_type: Type[T],
    ) -> Union[T, Exception]:
        """Validate a single contract.

        Args:
            contract: Dictionary to validate
            contract_type: Type of contract to validate against

        Returns:
            Validated contract or Exception if validation fails
        """
        validators = {
            AssetContract: validate_asset,
            LabelContract: validate_label,
            ProjectContract: validate_project,
            UserContract: validate_user,
        }

        validator = validators.get(contract_type)
        if not validator:
            raise ValueError(f"Unknown contract type: {contract_type}")

        try:
            return validator(contract)  # type: ignore
        except Exception as e:  # pylint: disable=broad-except
            return e
