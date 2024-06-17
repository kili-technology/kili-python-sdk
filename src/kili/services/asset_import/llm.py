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
from .exceptions import ImportFileConversionError, ImportValidationError
from .helpers import is_chat_format, process_json
from .types import AssetLike


class LLMDataType(Enum):
    """LLM data type."""

    DICT = "DICT"
    LIST = "LIST"
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
        if all(isinstance(content, list) for content in content_array):
            return LLMDataType.LIST
        raise ImportValidationError("Invalid value in content for LLM project.")

    @staticmethod
    def transform_asset_content(asset_content, json_metadata):
        """Transform asset content."""
        content, additional_json_metadata = process_json(asset_content)
        transformed_asset_content = json.dumps(content).encode("utf-8")

        json_metadata_dict = {}
        if json_metadata and isinstance(json_metadata, str):
            json_metadata_dict = json.loads(json_metadata)
        elif json_metadata:
            json_metadata_dict = json_metadata

        merged_json_metadata = {
            **json_metadata_dict,
            **additional_json_metadata,
        }
        changed_json_metadata = json.dumps(merged_json_metadata)

        return transformed_asset_content, changed_json_metadata

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
            for asset in assets:
                file_path = asset.get("content", None)
                json_metadata = asset.get("json_metadata", "{}")
                if file_path and isinstance(file_path, str):
                    try:
                        with open(file_path, encoding="utf-8") as file:
                            data = json.load(file)

                            if is_chat_format(data, {"role", "content", "id", "chat_id", "model"}):
                                (
                                    asset["content"],
                                    asset["json_metadata"],
                                ) = self.transform_asset_content(data, json_metadata)

                                batch_importer = JSONBatchImporter(
                                    self.kili, self.project_params, batch_params, self.pbar
                                )

                    except Exception as exception:
                        raise ImportFileConversionError(
                            f"Error processing file: {exception}"
                        ) from exception

        elif data_type == LLMDataType.HOSTED_FILE:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        elif data_type in (LLMDataType.DICT, LLMDataType.LIST):
            for asset in assets:
                if "content" in asset and isinstance(asset["content"], dict):
                    asset["content"] = json.dumps(asset["content"]).encode("utf-8")
                elif (
                    "content" in asset
                    and isinstance(asset["content"], list)
                    and is_chat_format(
                        asset["content"], {"role", "content", "id", "chat_id", "model"}
                    )
                ):
                    json_metadata = asset.get("json_metadata", "{}")
                    asset["content"], asset["json_metadata"] = self.transform_asset_content(
                        asset["content"], json_metadata
                    )

            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = JSONBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        else:
            raise ImportValidationError
        return self.import_assets_by_batch(assets, batch_importer)
