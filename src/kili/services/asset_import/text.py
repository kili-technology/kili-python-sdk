"""
Functions to import assets into a TEXT project
"""
import os
from enum import Enum
from typing import List, Optional, Tuple

from kili.helpers import is_url

from .base import (
    BaseAssetImporter,
    BatchParams,
    ContentBatchImporter,
    JsonContentBatchImporter,
)
from .exceptions import ImportValidationError
from .types import AssetLike


class TextDataType(Enum):
    """
    Text data type
    """

    RICH_TEXT = "RICH_TEXT"
    LOCAL_FILE = "LOCAL_FILE"
    HOSTED_FILE = "HOSTED_FILE"
    RAW_TEXT = "RAW_TEXT"


class RawTextBatchImporter(ContentBatchImporter):
    """
    class for importing a batch of raw text assets into a TEXT project
    """

    def get_content_type_and_data_from_content(self, content: Optional[str]) -> Tuple[str, str]:
        """
        Returns the data of the content (path) and its content type
        """
        return content or "", "text/plain"


class TextDataImporter(BaseAssetImporter):
    """
    Class for importing data into a TEXT project
    """

    @staticmethod
    def get_data_type(assets: List[AssetLike]) -> TextDataType:
        """
        Determine the type of data to upload from the service payload
        """
        content_array = [asset.get("content", "") for asset in assets]
        has_local_file = any(os.path.exists(content) for content in content_array)
        has_hosted_file = any(is_url(content) for content in content_array)
        has_json_content = any(asset.get("json_content") for asset in assets)
        if has_json_content:
            if any(content_array):
                raise ImportValidationError(
                    "Cannot import content when importing a Rich Text asset"
                )
            return TextDataType.RICH_TEXT
        if has_local_file and has_hosted_file:
            raise ImportValidationError(
                """
                Cannot upload hosted data and local files at the same time.
                Please separate the assets into 2 calls
                """
            )
        if has_local_file:
            return TextDataType.LOCAL_FILE
        if has_hosted_file:
            return TextDataType.HOSTED_FILE
        return TextDataType.RAW_TEXT

    def import_assets(self, assets: List[AssetLike]):
        """
        Import TEXT assets into Kili.
        """
        data_type = self.get_data_type(assets)
        assets = self.filter_duplicate_external_ids(assets)
        if data_type == TextDataType.LOCAL_FILE:
            assets = self.filter_local_assets(assets, self.raise_error)
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == TextDataType.HOSTED_FILE:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == TextDataType.RAW_TEXT:
            for asset in assets:
                if "content" in asset and isinstance(asset["content"], str):
                    asset["content"] = asset["content"].encode("utf-8")

            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = RawTextBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == TextDataType.RICH_TEXT:
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = JsonContentBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        else:
            raise ImportValidationError
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
