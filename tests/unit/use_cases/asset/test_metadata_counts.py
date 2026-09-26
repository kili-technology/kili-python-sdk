"""Tests for the metadata count use cases."""

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId
from kili.use_cases.asset import AssetUseCases


def test_count_assets_by_metadata_value_rejects_an_empty_key(kili_api_gateway: KiliAPIGateway):
    with pytest.raises(ValueError, match="top-level metadata key"):
        AssetUseCases(kili_api_gateway).count_assets_by_metadata_value(
            AssetFilters(project_id=ProjectId("project_id")), ""
        )

    kili_api_gateway.count_assets_by_metadata_value.assert_not_called()


def test_count_assets_by_metadata_value_validates_the_category_search(
    kili_api_gateway: KiliAPIGateway,
):
    with pytest.raises(ValueError):
        AssetUseCases(kili_api_gateway).count_assets_by_metadata_value(
            AssetFilters(project_id=ProjectId("project_id"), label_category_search="JOB."),
            "camera",
        )

    kili_api_gateway.count_assets_by_metadata_value.assert_not_called()


def test_list_assets_metadata_keys_calls_the_gateway(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.list_assets_metadata_keys.return_value = ["camera"]
    filters = AssetFilters(project_id=ProjectId("project_id"))

    keys = AssetUseCases(kili_api_gateway).list_assets_metadata_keys(filters)

    assert keys == ["camera"]
    kili_api_gateway.list_assets_metadata_keys.assert_called_once_with(filters)
