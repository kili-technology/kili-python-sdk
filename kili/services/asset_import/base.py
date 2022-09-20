"""
Common and generic functions to import files into a project
"""
import mimetypes
import pathlib
from abc import ABC, abstractmethod
from json import dumps
from typing import Callable, List, NamedTuple

from tqdm import tqdm

from kili.authentication import KiliAuth
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
    project_compatible_mimetypes,
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


class BaseBatchImporter:  # pylint: disable=too-few-public-methods
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

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Common actions to import a batch of asset
        """
        assets = self.loop_on_batch(self.stringify_metadata)(assets)
        assets = self.loop_on_batch(self.fill_empty_fields)(assets)
        result_batch = self.import_to_kili(assets)
        self.pbar.update(n=len(assets))
        return result_batch

    @staticmethod
    def stringify_metadata(asset: AssetLike) -> AssetLike:
        """
        Process the metadata field
        """
        json_metadata = asset.get("json_metadata", {})
        if not isinstance(json_metadata, str):
            json_metadata = dumps(json_metadata)
        return {**asset, "json_metadata": json_metadata}

    @staticmethod
    def fill_empty_fields(asset: AssetLike):
        """
        fill empty fields with their default value
        """
        field_names = ASSET_FIELDS_DEFAULT_VALUE.keys()
        return {
            field: asset.get(field) or ASSET_FIELDS_DEFAULT_VALUE[field] for field in field_names
        }

    @staticmethod
    def loop_on_batch(func: Callable):
        def loop_func(assets: list):
            return [func(asset) for asset in assets]

        return loop_func

    def _async_import_to_kili(self, assets: List[KiliResolverAsset]):
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

    def _sync_import_to_kili(self, assets: List[KiliResolverAsset]):
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
            return self._async_import_to_kili(assets)
        return self._sync_import_to_kili(assets)


class ContentBatchImporter(BaseBatchImporter):
    """
    Base class defining the import of a batch of assets that have content
    """

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Base method to import a batch of asset
        """
        if not self.is_hosted:
            assets = self.upload_local_content_to_bucket(assets)
        return super().import_batch(assets)

    def upload_local_content_to_bucket(self, assets: List[AssetLike]):
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
            content_type, _ = mimetypes.guess_type(path)
            assert content_type
            uploaded_content_url = bucket.upload_data_via_rest(signed_urls[i], data, content_type)
            uploaded_assets.append({**asset, "content": uploaded_content_url})
        return uploaded_assets


class JsonContentBatchImporter(BaseBatchImporter):
    """
    Base class defining the import of a batch of assets that have json_content
    """

    def stringify_json_content(self, asset) -> AssetLike:
        json_content = asset.get("json_content", {})
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return {**asset, "json_content": json_content}

    def upload_json_content_to_bucket(self, assets):
        signed_urls = bucket.request_signed_urls(self.auth, self.project_id, len(assets))
        uploaded_assets = []
        for i, asset in enumerate(assets):
            json_content = asset.get("json_content")
            uploaded_json_content_url = bucket.upload_data_via_rest(
                signed_urls[i], json_content, "text/plain"
            )
            uploaded_assets.append({**asset, "json_content": uploaded_json_content_url})
        return uploaded_assets

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Base method to import a batch of asset with json content
        """
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets = self.upload_json_content_to_bucket(assets)
        return super().import_batch(assets)


class BaseAssetImporter(ABC):
    """
    Base class for data importers
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

    @staticmethod
    def is_hosted_content(assets: List[AssetLike]):
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
                Please separate the assets into 2 calls
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
            try:
                self.check_file_exists(path)
                self.check_mime_type_compatibility(path)
                filtered_assets.append({**asset, "content": path})
            except Exception as err:
                if raise_error:
                    raise err
        if len(filtered_assets) == 0:
            raise ImportValidationError(
                """
                No files to upload.
                Check that the paths exist and file types are compatible with the project
                """
            )
        return filtered_assets

    @staticmethod
    def check_file_exists(path: pathlib.Path):
        """
        Check that the local file exists
        Return an error if it doesn't exist and raise_error is True
        """
        if not path.is_file():
            raise FileNotFoundError(f"file {path} does not exist")
        return True

    def check_mime_type_compatibility(self, path: pathlib.Path):
        """
        Check that the mimetype of a local file is compatible with the project input type.
        Return an error if the asset is not compatible and raise_error is True.
        """
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        input_type = self.project_params.input_type
        if mime_type not in project_compatible_mimetypes[input_type]:  # type: ignore
            raise MimeTypeError(
                f"""
                File mime type for {path} is {mime_type} and does not correspond
                to the type of the project.
                File mime type should be one of {project_compatible_mimetypes[input_type]}
                """
            )
        return True

    def import_assets_by_batch(self, assets: List[AssetLike], batch_importer: BaseBatchImporter):
        """
        import assets by batch with a given batch importer
        """
        batch_generator = pagination.batch_iterator_builder(assets, IMPORT_BATCH_SIZE)
        self.pbar.total = len(assets)
        self.pbar.refresh()
        for batch_assets in batch_generator:
            response = batch_importer.import_batch(batch_assets)
        return response
