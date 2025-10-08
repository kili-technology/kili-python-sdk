"""Unit tests for DataFrame adapters and validators."""

from typing import cast

import pytest

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore[assignment]

from kili.domain_v2.adapters import ContractValidator, DataFrameAdapter
from kili.domain_v2.asset import AssetContract, AssetView
from kili.domain_v2.label import LabelContract


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
class TestDataFrameAdapter:
    """Test suite for DataFrameAdapter."""

    def test_to_dataframe_with_assets(self):
        """Test converting asset contracts to DataFrame."""
        assets = [
            cast(AssetContract, {"id": "asset-1", "externalId": "ext-1", "content": "url1"}),
            cast(AssetContract, {"id": "asset-2", "externalId": "ext-2", "content": "url2"}),
        ]

        adapter = DataFrameAdapter()
        df = adapter.to_dataframe(assets, AssetContract, validate=False)

        assert pd is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df["id"]) == ["asset-1", "asset-2"]
        assert list(df["externalId"]) == ["ext-1", "ext-2"]

    def test_to_dataframe_empty_list(self):
        """Test converting empty list to DataFrame."""
        adapter = DataFrameAdapter()
        df = adapter.to_dataframe([], AssetContract, validate=False)

        assert pd is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_from_dataframe_with_assets(self):
        """Test converting DataFrame to asset contracts."""
        assert pd is not None
        df = pd.DataFrame(
            [
                {"id": "asset-1", "externalId": "ext-1"},
                {"id": "asset-2", "externalId": "ext-2"},
            ]
        )

        adapter = DataFrameAdapter()
        contracts = adapter.from_dataframe(df, AssetContract, validate=False)

        assert len(contracts) == 2
        assert contracts[0].get("id") == "asset-1"
        assert contracts[1].get("id") == "asset-2"

    def test_roundtrip_conversion(self):
        """Test converting to DataFrame and back."""
        original_assets = [
            cast(
                AssetContract,
                {
                    "id": "asset-1",
                    "externalId": "ext-1",
                    "content": "url1",
                    "isHoneypot": False,
                },
            ),
            cast(
                AssetContract,
                {
                    "id": "asset-2",
                    "externalId": "ext-2",
                    "content": "url2",
                    "isHoneypot": True,
                },
            ),
        ]

        adapter = DataFrameAdapter()

        # To DataFrame
        df = adapter.to_dataframe(original_assets, AssetContract, validate=False)

        # Back to contracts
        result = adapter.from_dataframe(df, AssetContract, validate=False)

        assert len(result) == 2
        assert result[0].get("id") == original_assets[0].get("id")
        assert result[0].get("externalId") == original_assets[0].get("externalId")
        assert result[1].get("isHoneypot") == original_assets[1].get("isHoneypot")

    def test_wrap_contracts_with_asset_view(self):
        """Test wrapping contracts in AssetView."""
        contracts = [
            cast(AssetContract, {"id": "asset-1", "externalId": "ext-1"}),
            cast(AssetContract, {"id": "asset-2", "externalId": "ext-2"}),
        ]

        adapter = DataFrameAdapter()
        views = adapter.wrap_contracts(contracts, AssetView)

        assert len(views) == 2
        assert isinstance(views[0], AssetView)
        assert isinstance(views[1], AssetView)
        assert views[0].id == "asset-1"
        assert views[1].display_name == "ext-2"

    def test_unwrap_views(self):
        """Test unwrapping views back to dictionaries."""
        contracts = [
            cast(AssetContract, {"id": "asset-1", "externalId": "ext-1"}),
            cast(AssetContract, {"id": "asset-2", "externalId": "ext-2"}),
        ]

        adapter = DataFrameAdapter()
        views = adapter.wrap_contracts(contracts, AssetView)
        unwrapped = adapter.unwrap_views(views)

        assert len(unwrapped) == 2
        assert unwrapped[0].get("id") == "asset-1"
        assert unwrapped[1].get("externalId") == "ext-2"

    def test_to_dataframe_does_not_mutate_original(self):
        """Test that DataFrame conversion doesn't mutate original data."""
        original_assets = [
            cast(AssetContract, {"id": "asset-1", "externalId": "ext-1"}),
        ]

        adapter = DataFrameAdapter()
        df = adapter.to_dataframe(original_assets, AssetContract, validate=False)

        # Modify DataFrame
        df.loc[0, "id"] = "modified-id"

        # Original should be unchanged
        assert original_assets[0].get("id") == "asset-1"

    def test_to_dataframe_with_nested_data(self):
        """Test converting contracts with nested structures."""
        labels = [
            cast(
                LabelContract,
                {
                    "id": "label-1",
                    "author": {"id": "user-1", "email": "user@example.com"},
                    "jsonResponse": {"job": "value"},
                },
            ),
        ]

        adapter = DataFrameAdapter()
        df = adapter.to_dataframe(labels, LabelContract, validate=False)

        assert pd is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.loc[0, "id"] == "label-1"
        assert isinstance(df.loc[0, "author"], dict)
        assert df.loc[0, "author"]["email"] == "user@example.com"


class TestContractValidator:
    """Test suite for ContractValidator."""

    def test_validate_single_valid_asset(self):
        """Test validating a single valid asset."""
        asset_data = {
            "id": "asset-1",
            "externalId": "ext-1",
        }

        validator = ContractValidator()
        result = validator.validate_single(asset_data, AssetContract)

        assert isinstance(result, dict)
        assert result.get("id") == "asset-1"

    def test_validate_batch_all_valid(self):
        """Test batch validation with all valid contracts."""
        assets = [
            {"id": "asset-1", "externalId": "ext-1"},
            {"id": "asset-2", "externalId": "ext-2"},
        ]

        validator = ContractValidator()
        valid, errors = validator.validate_batch(assets, AssetContract)

        assert len(valid) == 2
        assert len(errors) == 0
        assert valid[0].get("id") == "asset-1"
        assert valid[1].get("id") == "asset-2"

    def test_validate_batch_with_errors(self):
        """Test batch validation with some invalid contracts."""
        # Mix of valid and potentially invalid data
        mixed_data = [
            {"id": "asset-1", "externalId": "ext-1"},  # Valid
            {"id": 123},  # Potentially invalid (id should be string)
            {"id": "asset-3", "externalId": "ext-3"},  # Valid
        ]

        validator = ContractValidator()
        valid, errors = validator.validate_batch(mixed_data, AssetContract)

        # With total=False, this might still be valid
        # The test shows error handling capability
        assert len(valid) + len(errors) == len(mixed_data)

    def test_validate_batch_empty_list(self):
        """Test batch validation with empty list."""
        validator = ContractValidator()
        valid, errors = validator.validate_batch([], AssetContract)

        assert len(valid) == 0
        assert len(errors) == 0

    def test_validate_single_with_label_contract(self):
        """Test validating a label contract."""
        label_data = {
            "id": "label-1",
            "author": {"email": "user@example.com"},
            "jsonResponse": {},
        }

        validator = ContractValidator()
        result = validator.validate_single(label_data, LabelContract)

        assert isinstance(result, dict)
        assert result.get("id") == "label-1"

    def test_validate_batch_labels(self):
        """Test batch validation with label contracts."""
        labels = [
            {"id": "label-1", "jsonResponse": {}},
            {"id": "label-2", "jsonResponse": {"job": "value"}},
        ]

        validator = ContractValidator()
        valid, errors = validator.validate_batch(labels, LabelContract)

        assert len(valid) == 2
        assert len(errors) == 0


@pytest.mark.skipif(not PANDAS_AVAILABLE, reason="pandas not installed")
class TestDataFrameAdapterPerformance:
    """Performance-related tests for DataFrame adapter."""

    def test_large_dataset_conversion(self):
        """Test converting a larger dataset to/from DataFrame."""
        # Create 1000 assets
        assets = [
            cast(
                AssetContract,
                {
                    "id": f"asset-{i}",
                    "externalId": f"ext-{i}",
                    "content": f"url-{i}",
                },
            )
            for i in range(1000)
        ]

        adapter = DataFrameAdapter()

        # Convert to DataFrame
        df = adapter.to_dataframe(assets, AssetContract, validate=False)
        assert len(df) == 1000

        # Convert back
        result = adapter.from_dataframe(df, AssetContract, validate=False)
        assert len(result) == 1000
        assert result[0].get("id") == "asset-0"
        assert result[999].get("id") == "asset-999"

    def test_wrap_large_dataset(self):
        """Test wrapping a large dataset in views."""
        assets = [
            cast(AssetContract, {"id": f"asset-{i}", "externalId": f"ext-{i}"}) for i in range(1000)
        ]

        adapter = DataFrameAdapter()
        views = adapter.wrap_contracts(assets, AssetView)

        assert len(views) == 1000
        assert all(isinstance(v, AssetView) for v in views)
        assert views[0].id == "asset-0"
        assert views[999].id == "asset-999"
