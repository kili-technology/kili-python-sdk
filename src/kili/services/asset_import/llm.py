"""Functions to import assets into a TEXT project."""

import json
import os
from enum import Enum
from typing import List, Optional, Tuple

from kili.core.helpers import is_url

from .base import (
    BaseAbstractAssetImporter,
    BatchParams,
    ContentBatchImporter,
)
from .exceptions import ImportValidationError
from .types import AssetLike


class LLMDataType(Enum):
    """LLM data type."""

    DICT = "DICT"
    LOCAL_FILE = "LOCAL_FILE"
    HOSTED_FILE = "HOSTED_FILE"


class JSONBatchImporter(ContentBatchImporter):
    """Class for importing a batch of LLM assets with dict content into a LLM_RLHF project."""

    def get_content_type_and_data_from_content(self, content: Optional[str]) -> Tuple[str, str]:
        """Returns the data of the content (path) and its content type."""
        return content or "", "application/json"


class LLMDataImporter(BaseAbstractAssetImporter):
    """Class for importing data into a TEXT project."""

    @staticmethod
    def get_data_type(assets: List[AssetLike]) -> LLMDataType:
        """Determine the type of data to upload from the service payload."""
        content_array = [asset.get("content", None) for asset in assets]
        if all(is_url(content) for content in content_array):
            return LLMDataType.HOSTED_FILE
        if all(isinstance(content, str) and os.path.exists(content) for content in content_array):
            return LLMDataType.LOCAL_FILE
        if all(isinstance(content, dict) for content in content_array):
            return LLMDataType.DICT
        raise ImportValidationError("Invalid value in content for LLM project.")

    def import_assets(self, assets: List[AssetLike]):
        """Import LLM assets into Kili."""
        self._check_upload_is_allowed(assets)
        data_type = self.get_data_type(assets)
        assets = self.filter_duplicate_external_ids(assets)
        if data_type == LLMDataType.LOCAL_FILE:
            assets = self.filter_local_assets(assets, self.raise_error)
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        elif data_type == LLMDataType.HOSTED_FILE:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        elif data_type == LLMDataType.DICT:
            for asset in assets:
                if "content" in asset and isinstance(asset["content"], dict):
                    asset["content"] = json.dumps(asset["content"]).encode("utf-8")
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = JSONBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        else:
            raise ImportValidationError
        return self.import_assets_by_batch(assets, batch_importer)
