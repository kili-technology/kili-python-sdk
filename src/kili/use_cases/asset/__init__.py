"""Asset use cases."""

import itertools
from typing import Generator, Literal, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.constants import QUERY_BATCH_SIZE
from kili.core.helpers import validate_category_search_query
from kili.core.utils.pagination import batcher
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.services.label_data_parsing.types import Project as LabelParsingProject
from kili.use_cases.asset.asset_label_parsing import parse_labels_of_asset
from kili.use_cases.asset.media_downloader import get_download_assets_function
from kili.use_cases.base import BaseUseCases


class AssetUseCases(BaseUseCases):
    """Asset use cases."""

    # pylint: disable=too-many-arguments
    def list_assets(
        self,
        filters: AssetFilters,
        fields: ListOrTuple[str],
        options: QueryOptions,
        download_media: bool,
        local_media_dir: Optional[str],
        label_output_format: Literal["dict", "parsed_label"],
    ) -> Generator:
        """List assets with given options."""
        if filters.label_category_search:
            validate_category_search_query(filters.label_category_search)

        download_media_function, fields = get_download_assets_function(
            self._kili_api_gateway,
            download_media,
            fields,
            ProjectId(filters.project_id),
            local_media_dir,
        )
        assets_gen = self._kili_api_gateway.list_assets(filters, fields, options)

        if download_media_function is not None:
            # TODO: modify download_media function so it can take a generator of assets
            assets_lists = [
                download_media_function(assets_batch)
                for assets_batch in batcher(assets_gen, QUERY_BATCH_SIZE)
            ]
            assets_gen = (asset for asset in itertools.chain(*assets_lists))

        if label_output_format == "parsed_label":
            project = LabelParsingProject(
                **self._kili_api_gateway.get_project(
                    ProjectId(filters.project_id), ("jsonInterface", "inputType")
                )
            )
            assets_gen = (parse_labels_of_asset(asset, project) for asset in assets_gen)

        return assets_gen

    def count_assets(self, filters: AssetFilters) -> int:
        """Send a GraphQL request calling countAssets resolver."""
        if filters.label_category_search:
            validate_category_search_query(filters.label_category_search)
        return self._kili_api_gateway.count_assets(filters)
