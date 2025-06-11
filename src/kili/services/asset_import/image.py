"""Functions to import assets into an IMAGE project."""

import os
from typing import List

from kili.core.constants import mime_extensions_that_need_post_processing
from kili.core.helpers import get_mime_type
from kili.domain.project import InputType

from .base import BaseAbstractAssetImporter, BatchParams, ContentBatchImporter
from .constants import LARGE_IMAGE_THRESHOLD_SIZE, MAX_WIDTH_OR_HEIGHT_NON_TILED
from .types import AssetLike


class ImageDataImporter(BaseAbstractAssetImporter):
    """Class for importing assets into an IMAGE or GEOSPATIAL project."""

    def import_assets(self, assets: List[AssetLike], input_type: InputType):
        """Import IMAGE assets into Kili."""
        self._check_upload_is_allowed(assets)
        is_hosted = self.is_hosted_content(assets)
        if not is_hosted:
            assets = self.filter_local_assets(assets, self.raise_error)
        assets = self.filter_duplicate_external_ids(assets)
        sync_assets, async_assets = self.split_asset_by_upload_type(assets, is_hosted)
        created_asset_ids: List[str] = []
        if len(sync_assets) > 0:
            sync_batch_params = BatchParams(
                is_hosted=is_hosted, is_asynchronous=False, input_type=input_type
            )
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, sync_batch_params, self.pbar
            )
            created_asset_ids += self.import_assets_by_batch(
                sync_assets, batch_importer, input_type=input_type
            )
        if len(async_assets) > 0:
            async_batch_params = BatchParams(
                is_hosted=is_hosted, is_asynchronous=True, input_type=input_type
            )
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, async_batch_params, self.pbar
            )
            created_asset_ids += self.import_assets_by_batch(
                async_assets, batch_importer, input_type=input_type
            )
        return created_asset_ids

    @staticmethod
    def get_is_large_image(image_path: str) -> bool:
        """Define if an image is too large and so on has to be tiled."""
        try:
            from PIL import Image  # pylint: disable=import-outside-toplevel

            Image.MAX_IMAGE_PIXELS = None
        except ImportError as e:
            raise ImportError("Install with `pip install kili[image]` to use this feature.") from e

        if os.path.getsize(image_path) >= LARGE_IMAGE_THRESHOLD_SIZE:
            return True

        image = Image.open(image_path)
        width, height = image.size
        return width >= MAX_WIDTH_OR_HEIGHT_NON_TILED or height >= MAX_WIDTH_OR_HEIGHT_NON_TILED

    @staticmethod
    def split_asset_by_upload_type(assets: List[AssetLike], is_hosted: bool):
        """Split assets into two groups, assets to to imported synchronously or asynchronously."""
        try:
            from PIL import UnidentifiedImageError  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            raise ImportError("Install with `pip install kili[image]` to use this feature.") from e
        if is_hosted:
            return assets, []
        sync_assets, async_assets = [], []
        for asset in assets:
            multi_layer_content = asset.get("multi_layer_content")
            if multi_layer_content is not None:
                async_assets.append(asset)
                continue
            json_content = asset.get("json_content")
            path = asset.get("content")
            if json_content and not path:
                sync_assets.append(asset)
                continue
            assert path
            assert isinstance(path, str)
            mime_type = get_mime_type(path)
            if mime_type in mime_extensions_that_need_post_processing:
                async_assets.append(asset)
            else:
                try:
                    is_large_image = ImageDataImporter.get_is_large_image(path)
                    if is_large_image:
                        async_assets.append(asset)
                    else:
                        sync_assets.append(asset)
                except UnidentifiedImageError:
                    async_assets.append(asset)
        return sync_assets, async_assets
