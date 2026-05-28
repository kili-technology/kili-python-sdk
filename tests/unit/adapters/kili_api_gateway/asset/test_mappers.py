"""Tests for asset_where_mapper in kili_api_gateway/asset/mappers.py."""

from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId


class TestAssetWhereMapperGroupName:
    """Tests for group_name field in asset_where_mapper."""

    def test_group_name_is_mapped_to_graphql_group_name(self):
        """group_name list is correctly mapped to groupName in the GQL where clause."""
        result = asset_where_mapper(AssetFilters(project_id=ProjectId("proj1"), group_name=["g1"]))
        assert result["groupName"] == ["g1"]

    def test_group_name_multiple_values(self):
        """Multiple group names are passed through unchanged."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name=["GroupA", "GroupB"])
        )
        assert result["groupName"] == ["GroupA", "GroupB"]

    def test_group_name_none_produces_none(self):
        """When group_name is None, groupName is None in the output."""
        result = asset_where_mapper(AssetFilters(project_id=ProjectId("proj1"), group_name=None))
        assert result["groupName"] is None

    def test_group_name_empty_list_produces_none(self):
        """Empty group_name list is normalised to None (falsy guard)."""
        result = asset_where_mapper(AssetFilters(project_id=ProjectId("proj1"), group_name=[]))
        assert result["groupName"] is None
