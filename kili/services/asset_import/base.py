"""
Common and generic functions to import files into a project
"""
import mimetypes
import pathlib
import time
from abc import ABC, abstractmethod
from json import dumps
from typing import List, NamedTuple

from tqdm import tqdm

from kili.authentication import KiliAuth
from kili.constants import THROTTLING_DELAY
from kili.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.helpers import format_result, is_url
from kili.orm import Asset
from kili.utils import bucket, pagination

from .constants import (
    ASSET_FIELDS_DEFAULT_VALUE,
    IMPORT_BATCH_SIZE,
    mime_extensions_for_IV2,
)
from .exceptions import ImportValidationError, MimeTypeError
from .types import AssetLike, KiliResolverAsset


class BatchParams(NamedTuple):
    """
    Contains all parameters related the batch to import
    """

    is_asynchronous: bool
    is_hosted: bool


class ProcessingParams(NamedTuple):
    """
    Contains all parameters related the assets processing
    """

    raise_error: bool


class ProjectParams(NamedTuple):
    """
    Contains all parameters related the batch to import
    """

    project_id: str
    input_type: str


class LoggerParams(NamedTuple):
    """
    Contains all parameters related the logging
    """

    disable_tqdm: bool


class AbstractAssetImporter(ABC):  # pylint: disable=too-few-public-methods
    """
    Abstract class for a data importer
    """

    def __init__(
        self,
        auth: KiliAuth,
        project_params: ProjectParams,
        processing_params: ProcessingParams,
        logger_params: LoggerParams,
    ):
        self.auth = auth
        self.project_params = project_params
        self.raise_error = processing_params.raise_error
        self.pbar = tqdm(disable=logger_params.disable_tqdm)

    @abstractmethod
    def import_assets(self, assets: List[AssetLike]):
        """
        Import the assets in Kili.
        """


class AbstractBatchImporter(ABC):  # pylint: disable=too-few-public-methods
    """
    Abstract class for a batch importer
    """

    def __init__(
        self, auth: KiliAuth, project_params: ProjectParams, batch_params: BatchParams, pbar: tqdm
    ):
        self.auth = auth
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type
        self.is_hosted = batch_params.is_hosted
        self.is_asynchronous = batch_params.is_asynchronous
        self.pbar = pbar

    @abstractmethod
    def import_batch(self, assets: List[AssetLike]):
        """
        Import the batch of assets in Kili
        """


class BaseBatchImporter(AbstractBatchImporter):
    """
    Base class defining the import of a batch of assets.
    """

    def import_batch(self, assets: List[AssetLike]):
        """
        Base method to import a batch of asset
        """
        batch_start = time.time()
        if not self.is_hosted:
            assets = self.upload_local_contents_to_bucket(assets)

        asset_batch_to_import = []
        for asset in assets:
            asset = self.stringify_json_variables(asset)
            asset = self.fill_empty_fields(asset)
            asset_batch_to_import.append(asset)
        result_batch = self.import_to_kili(asset_batch_to_import)
        self.pbar.update(n=len(assets))
        batch_time = time.time() - batch_start
        if batch_time < THROTTLING_DELAY:
            time.sleep(THROTTLING_DELAY - batch_time)
        return result_batch

    @staticmethod
    def stringify_json_variables(asset: AssetLike) -> AssetLike:
        """
        Stringify the json content and the json metadata
        """
        json_metadata = asset.get("json_metadata")
        json_content = asset.get("json_content")
        if isinstance(json_metadata, dict):
            json_metadata = dumps(json_metadata)
        if isinstance(json_content, dict):
            json_content = dumps(json_content)
        return {**asset, "json_content": json_content, "json_metadata": json_metadata}

    @staticmethod
    def fill_empty_fields(asset: AssetLike):
        """
        fill empty fields with their default value
        """
        field_names = ASSET_FIELDS_DEFAULT_VALUE.keys()
        return {
            field: asset.get(field) or ASSET_FIELDS_DEFAULT_VALUE[field] for field in field_names
        }

    def upload_local_contents_to_bucket(self, assets: List[AssetLike]):
        """
        Upload local data to a bucket
        """
        signed_urls = bucket.request_signed_urls(self.auth, self.project_id, len(assets))
        uploaded_assets = []
        for i, asset in enumerate(assets):
            path = asset.get("content")
            assert path
            with open(path, "rb") as file:
                data = file.read()
            content_type, _ = mimetypes.guess_type(path.lower())
            assert content_type
            uploaded_content_url = bucket.upload_data_via_rest(signed_urls[i], data, content_type)
            uploaded_assets.append({**asset, "content": uploaded_content_url})
        return uploaded_assets

    def async_import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets with asynchronous resolver.
        """
        upload_type = "GEO_SATELLITE" if self.input_type == "IMAGE" else "VIDEO"
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
                "uploadType": upload_type,
            },
            "where": {"id": self.project_id},
        }
        results = self.auth.client.execute(GQL_APPEND_MANY_FRAMES_TO_DATASET, payload)
        return format_result("data", results, Asset)

    def sync_import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets with synchronous resolver
        """
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "isHoneypotArray": [asset["is_honeypot"] for asset in assets],
                "statusArray": [asset["status"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
            },
            "where": {"id": self.project_id},
        }
        results = self.auth.client.execute(GQL_APPEND_MANY_TO_DATASET, payload)
        return format_result("data", results, Asset)

    def import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets to Kili with the right resolver
        """
        if self.is_asynchronous:
            return self.async_import_to_kili(assets)
        return self.sync_import_to_kili(assets)


class BaseAssetImporter(AbstractAssetImporter):
    """ "
    Base class for data importers
    """

    @staticmethod
    def is_hosted_data(assets: List[AssetLike]):
        """
        Determine if the assets to upload are from local files or hosted data
        Raise an error if a mix of both
        """
        contents = [asset.get("content") for asset in assets]
        if all(is_url(content) for content in contents):
            return True
        if any(is_url(content) for content in contents):
            raise ImportValidationError(
                """
                Cannot upload hosted data and local files at the same time.
                Please separete the assets into 2 calls
                """
            )
        return False

    def filter_local_assets(self, assets: List[AssetLike], raise_error: bool):
        """
        Filter out local files that cannot be imported.
        Return an error at the first file that cannot be imported if raise_error is True
        """
        filtered_assets = []
        for asset in assets:
            path = asset.get("content")
            if path is None:
                continue
            path = pathlib.Path(path)
            file_exists = self.check_file_exists(path, raise_error)
            has_right_mime_type = self.check_mime_type_compatibility(path, raise_error)
            if path and file_exists and has_right_mime_type:
                filtered_assets.append({**asset, "content": path})
        return filtered_assets

    @staticmethod
    def check_file_exists(path: pathlib.Path, raise_error: bool):
        """
        Check that the local file exists
        Return an error if it doesn't exist and raise_error is True
        """
        file_exists = True
        if not path.is_file():
            file_exists = False
            if raise_error:
                raise FileNotFoundError(f"file {path} does not exist")
        return file_exists

    def check_mime_type_compatibility(self, path: pathlib.Path, raise_error: bool):
        """
        Check that the mimetype of a local file is compatible with the project input type.
        Return an error if the asset is not compatible and raise_error is True.
        """
        mime_type, _ = mimetypes.guess_type(path)
        correct_mime_type = True
        if mime_type is None:
            correct_mime_type = False
            if raise_error:
                raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        input_type = self.project_params.input_type
        if mime_type not in mime_extensions_for_IV2[input_type]:  # type: ignore
            correct_mime_type = False
            if raise_error:
                raise MimeTypeError(
                    f"""
                    File mime type for {path} is {mime_type} and does not correspond
                    to the type of the project.
                    File mime type should be one of {mime_extensions_for_IV2[input_type]}
                    """
                )

        return correct_mime_type

    def import_assets_by_batch(
        self, assets: List[AssetLike], batch_importer: AbstractBatchImporter
    ):
        """
        import assets by batch with a given batch importer
        """
        batch_generator = pagination.batch_iterator_builder(assets, IMPORT_BATCH_SIZE)
        self.pbar.total = len(assets)
        self.pbar.refresh()
        for batch_assets in batch_generator:
            response = batch_importer.import_batch(batch_assets)
        return response
