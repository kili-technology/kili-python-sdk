"""Integration tests for AssetView objects returned by the assets namespace.

This test file validates that the assets.list() method correctly returns
AssetView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns AssetView objects in all modes (list, generator, DataFrame)
    - Test AssetView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Ensure DataFrame mode remains unchanged
"""

import pytest

from kili.domain_v2.asset import AssetView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_asset_views(kili_client):
    """Test that assets.list() in list mode returns AssetView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get assets in list mode
    assets = kili_client.assets.list(project_id=project_id, first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(assets, list), "assets.list() with as_generator=False should return a list"

    # Skip if no assets
    if not assets:
        pytest.skip(f"No assets available in project {project_id}")

    # Verify each item is an AssetView
    for asset in assets:
        assert_is_view(asset, AssetView)

        # Verify we can access basic properties
        assert hasattr(asset, "id")
        assert hasattr(asset, "external_id")
        assert hasattr(asset, "display_name")


@pytest.mark.integration()
def test_list_generator_returns_asset_views(kili_client):
    """Test that assets.list() in generator mode returns AssetView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get assets in generator mode
    assets_gen = kili_client.assets.list(project_id=project_id, first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    assets_from_gen = []
    for i, asset in enumerate(assets_gen):
        if i >= 5:
            break
        assets_from_gen.append(asset)

    # Skip if no assets
    if not assets_from_gen:
        pytest.skip(f"No assets available in project {project_id}")

    # Verify each yielded item is an AssetView
    for asset in assets_from_gen:
        assert_is_view(asset, AssetView)

        # Verify we can access basic properties
        assert hasattr(asset, "id")
        assert hasattr(asset, "external_id")


@pytest.mark.integration()
def test_asset_view_properties(kili_client):
    """Test that AssetView provides access to all expected properties."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get first asset
    assets = kili_client.assets.list(project_id=project_id, first=1, as_generator=False)

    if not assets:
        pytest.skip(f"No assets available in project {project_id}")

    asset = assets[0]

    # Verify AssetView type
    assert_is_view(asset, AssetView)

    # Test core properties exist and are accessible
    assert_view_property_access(asset, "id")
    assert_view_property_access(asset, "external_id")
    assert_view_property_access(asset, "content")
    assert_view_property_access(asset, "display_name")

    # Test that id is not empty
    assert asset.id, "Asset id should not be empty"

    # Test display_name logic (should be external_id if available, else id)
    if asset.external_id:
        assert asset.display_name == asset.external_id
    else:
        assert asset.display_name == asset.id

    # Test optional properties
    assert_view_property_access(asset, "metadata")
    assert_view_property_access(asset, "labels")
    assert_view_property_access(asset, "latest_label")
    assert_view_property_access(asset, "status")
    assert_view_property_access(asset, "current_step")
    assert_view_property_access(asset, "is_honeypot")
    assert_view_property_access(asset, "skipped")
    assert_view_property_access(asset, "created_at")

    # Test computed properties
    assert_view_property_access(asset, "has_labels")
    assert_view_property_access(asset, "label_count")

    # Verify labels is a list
    assert isinstance(asset.labels, list), "labels property should return a list"

    # Verify label_count matches labels length
    assert asset.label_count == len(asset.labels), "label_count should match length of labels"

    # Verify has_labels is consistent with label_count
    assert asset.has_labels == (asset.label_count > 0), "has_labels should match label_count > 0"


@pytest.mark.integration()
def test_asset_view_dict_compatibility(kili_client):
    """Test that AssetView maintains backward compatibility via to_dict()."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get first asset
    assets = kili_client.assets.list(project_id=project_id, first=1, as_generator=False)

    if not assets:
        pytest.skip(f"No assets available in project {project_id}")

    asset = assets[0]

    # Verify AssetView type
    assert_is_view(asset, AssetView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(asset)

    # Get dictionary representation
    asset_dict = asset.to_dict()

    # Verify it's a dictionary
    assert isinstance(asset_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in asset_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "externalId" in asset_dict:
        assert (
            asset_dict["externalId"] == asset.external_id
        ), "Dictionary externalId should match property"

    if "content" in asset_dict:
        assert asset_dict["content"] == asset.content, "Dictionary content should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert asset_dict is asset._data, "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_asset_view_with_dataframe(kili_client):
    """Test that DataFrame mode still returns DataFrame (unchanged behavior)."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Check if pandas is available
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("pandas not available, skipping DataFrame test")

    # Get assets in DataFrame mode
    assets_df = kili_client.assets.list(
        project_id=project_id, first=5, as_generator=False, format="pandas"
    )

    # Verify we get a DataFrame
    assert isinstance(
        assets_df, pd.DataFrame
    ), "assets.list() with format='pandas' should return DataFrame"

    # Verify DataFrame has expected structure
    if not assets_df.empty:
        # DataFrame should have 'id' column
        assert "id" in assets_df.columns, "DataFrame should have 'id' column"


@pytest.mark.integration()
def test_asset_view_filtering(kili_client):
    """Test that AssetView objects work correctly with filtering."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get all assets
    all_assets = kili_client.assets.list(project_id=project_id, first=10, as_generator=False)

    if not all_assets:
        pytest.skip(f"No assets available in project {project_id}")

    # Get the first asset's ID
    first_asset_id = all_assets[0].id

    # Query for specific asset by ID
    filtered_assets = kili_client.assets.list(
        project_id=project_id, asset_id=first_asset_id, as_generator=False
    )

    # Verify we got results
    assert len(filtered_assets) > 0, "Should get at least one asset with specific asset_id"

    # Verify each result is an AssetView
    for asset in filtered_assets:
        assert_is_view(asset, AssetView)

        # Verify it's the correct asset
        assert asset.id == first_asset_id, "Filtered asset should have the requested ID"


@pytest.mark.integration()
def test_asset_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Query with a filter that should return no results
    # Using a non-existent asset ID
    empty_assets = kili_client.assets.list(
        project_id=project_id, asset_id="non-existent-asset-id-12345", as_generator=False
    )

    # Verify we get an empty list
    assert isinstance(empty_assets, list), "Should return a list even when no results"
    assert len(empty_assets) == 0, "Should return empty list for non-existent asset"


@pytest.mark.integration()
def test_asset_view_with_fields_parameter(kili_client):
    """Test that AssetView works correctly with custom fields parameter."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Query with specific fields
    assets = kili_client.assets.list(
        project_id=project_id, first=1, fields=["id", "externalId", "content"], as_generator=False
    )

    if not assets:
        pytest.skip(f"No assets available in project {project_id}")

    asset = assets[0]

    # Verify it's still an AssetView
    assert_is_view(asset, AssetView)

    # Verify requested fields are accessible
    assert_view_property_access(asset, "id")
    assert_view_property_access(asset, "external_id")
    assert_view_property_access(asset, "content")
