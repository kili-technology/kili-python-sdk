"""Asset use cases."""


from typing import List, Literal, Optional

from kili.core.helpers import validate_category_search_query
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.gateways.kili_api_gateway.asset.types import AssetWhere
from kili.gateways.kili_api_gateway.queries import QueryOptions
from kili.services.label_data_parsing.types import Project as LabelParsingProject
from kili.use_cases.asset.asset_label_parsing import parse_labels_of_asset
from kili.use_cases.asset.media_downloader import get_download_assets_function


class AssetUseCases:
    """Asset use cases."""

    def __init__(self, kili_api_gateway: KiliAPIGateway):
        self._kili_api_gateway = kili_api_gateway

    # pylint: disable=too-many-arguments
    def list_assets(
        self,
        where: AssetWhere,
        fields: List[str],
        options: QueryOptions,
        download_media: bool,
        local_media_dir: Optional[str],
        label_output_format: Literal["dict", "parsed_label"],
    ):
        """List assets with given options."""

        if where.label_category_search:
            validate_category_search_query(where.label_category_search)

        post_call_function, fields = get_download_assets_function(
            self._kili_api_gateway, download_media, fields, where.project_id, local_media_dir
        )
        assets_gen = self._kili_api_gateway.list_assets(fields, where, options, post_call_function)

        if label_output_format == "parsed_label":
            project: LabelParsingProject = self._kili_api_gateway.get_project(
                where.project_id, ["jsonInterface", "inputType"]
            )
            assets_gen = (parse_labels_of_asset(asset, project) for asset in assets_gen)

        return assets_gen

    def count_assets(self, where: AssetWhere) -> int:
        """Send a GraphQL request calling countAssets resolver."""
        if where.label_category_search:
            validate_category_search_query(where.label_category_search)
        return self._kili_api_gateway.count_assets(where)
