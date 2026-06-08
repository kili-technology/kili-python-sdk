"""Tests for asset_where_mapper in kili_api_gateway/asset/mappers.py."""

from kili.adapters.kili_api_gateway.asset.mappers import asset_where_mapper
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId


class TestAssetWhereMapperGroupName:
    """Tests for group_name_in field in asset_where_mapper."""

    def test_group_name_in_is_mapped_to_graphql_group_name_in(self):
        """group_name_in list is correctly mapped to groupNameIn in the GQL where clause."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_in=["g1"])
        )
        assert result["groupNameIn"] == ["g1"]

    def test_group_name_in_multiple_values(self):
        """Multiple group names are passed through unchanged."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_in=["GroupA", "GroupB"])
        )
        assert result["groupNameIn"] == ["GroupA", "GroupB"]

    def test_group_name_in_none_produces_none(self):
        """When group_name_in is None, groupNameIn is None in the output."""
        result = asset_where_mapper(AssetFilters(project_id=ProjectId("proj1"), group_name_in=None))
        assert result["groupNameIn"] is None

    def test_group_name_in_empty_list_produces_none(self):
        """Empty group_name_in list is normalised to None (falsy guard)."""
        result = asset_where_mapper(AssetFilters(project_id=ProjectId("proj1"), group_name_in=[]))
        assert result["groupNameIn"] is None

    def test_group_name_not_in_is_mapped_to_graphql_group_name_not_in(self):
        """group_name_not_in list is correctly mapped to groupNameNotIn in the GQL where clause."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_not_in=["g1"])
        )
        assert result["groupNameNotIn"] == ["g1"]

    def test_group_name_not_in_multiple_values(self):
        """Multiple excluded group names are passed through unchanged."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_not_in=["GroupA", "GroupB"])
        )
        assert result["groupNameNotIn"] == ["GroupA", "GroupB"]

    def test_group_name_not_in_none_produces_none(self):
        """When group_name_not_in is None, groupNameNotIn is None in the output."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_not_in=None)
        )
        assert result["groupNameNotIn"] is None

    def test_group_name_not_in_empty_list_produces_none(self):
        """Empty group_name_not_in list is normalised to None (falsy guard)."""
        result = asset_where_mapper(
            AssetFilters(project_id=ProjectId("proj1"), group_name_not_in=[])
        )
        assert result["groupNameNotIn"] is None
