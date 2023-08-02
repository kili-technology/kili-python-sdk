"""Common and generic functions to import files into a project."""
import abc
import logging
import mimetypes
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from json import dumps
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Tuple, Union
from uuid import uuid4

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_exponential

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_ASSETS,
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
)
from kili.core.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.core.graphql.operations.organization.queries import (
    OrganizationQuery,
    OrganizationWhere,
)
from kili.core.helpers import RetryLongWaitWarner, T, format_result, is_url
from kili.core.utils import pagination
from kili.orm import Asset
from kili.services.asset_import.constants import (
    IMPORT_BATCH_SIZE,
    project_compatible_mimetypes,
)
from kili.services.asset_import.exceptions import (
    BatchImportError,
    ImportValidationError,
    MimeTypeError,
    UploadFromLocalDataForbiddenError,
)
from kili.services.asset_import.types import AssetLike, KiliResolverAsset
from kili.utils import bucket
from kili.utils.tqdm import tqdm


class BatchParams(NamedTuple):
    """Contains all parameters related to the batch to import."""

    is_asynchronous: bool
    is_hosted: bool


class ProcessingParams(NamedTuple):
    """Contains all parameters related to the assets processing."""

    raise_error: bool
    verify: bool


class ProjectParams(NamedTuple):
    """Contains all parameters related to the batch to import."""

    project_id: str
    input_type: str


class LoggerParams(NamedTuple):
    """Contains all parameters related to logging."""

    disable_tqdm: bool


class BaseBatchImporter:  # pylint: disable=too-many-instance-attributes
    """Base class for BatchImporters."""

    def __init__(self, kili, project_params: ProjectParams, batch_params: BatchParams, pbar: tqdm):
        self.kili = kili
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type
        self.is_hosted = batch_params.is_hosted
        self.is_asynchronous = batch_params.is_asynchronous
        self.pbar = pbar
        self.http_client = kili.http_client

        logging.basicConfig()
        self.logger = logging.getLogger("kili.services.asset_import.base")
        self.logger.setLevel(logging.INFO)

    def import_batch(self, assets: List[AssetLike], verify: bool) -> List[str]:
        """Base actions to import a batch of asset.

        returns:
            created_assets_ids: list of ids of the created assets
        """
        assets = self.loop_on_batch(self.stringify_metadata)(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets_ = self.loop_on_batch(self.fill_empty_fields)(assets)
        created_assets_ids = self.import_to_kili(assets_)
        if verify:
            self.verify_batch_imported(assets)
        self.pbar.update(n=len(assets))
        return created_assets_ids

    def verify_batch_imported(self, assets: List):
        """Verifies that the batch has been imported successfully."""
        if self.is_asynchronous:
            logger_func = self.logger.info
            log_message = (
                "Import of assets is taking a long time to complete. This maybe be due to files"
                " being processed by the server."
            )
        else:
            logger_func = self.logger.warning
            log_message = (
                "Import of assets is taking a long time to complete. This may be due to a large"
                " number of assets to be processed by the server."
            )
        for attempt in Retrying(
            retry=retry_if_exception_type(BatchImportError),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            before_sleep=RetryLongWaitWarner(logger_func=logger_func, warn_message=log_message),
            reraise=True,
        ):
            with attempt:
                assets_ids = [assets[-1]["id"]]  # check last asset of the batch only
                where = AssetWhere(project_id=self.project_id, asset_id_in=assets_ids)
                nb_assets_in_kili = AssetQuery(
                    self.kili.graphql_client, self.kili.http_client
                ).count(where)
                if len(assets_ids) != nb_assets_in_kili:
                    raise BatchImportError(
                        "Number of assets to upload is not equal to number of assets uploaded in"
                        " Kili."
                    )

    def add_ids(self, assets: List[AssetLike]):
        """Adds ids to all assets."""
        return self.loop_on_batch(self.add_id_to_asset)(assets)

    def generate_project_bucket_path(self) -> str:
        """Returns ids."""
        return f"projects/{self.project_id}/assets"

    @staticmethod
    def stringify_metadata(asset: AssetLike) -> AssetLike:
        """Stringify the metadata."""
        json_metadata = asset.get("json_metadata", {})
        if not isinstance(json_metadata, str):
            json_metadata = dumps(json_metadata)
        return {**asset, "json_metadata": json_metadata}

    @staticmethod
    def stringify_json_content(asset: AssetLike) -> AssetLike:
        """Stringify the metadata."""
        json_content = asset.get("json_content", "")
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return {**asset, "json_content": json_content}

    @staticmethod
    def add_id_to_asset(asset: AssetLike) -> AssetLike:
        """Generates an asset id."""
        return {**asset, "id": asset.get("id", bucket.generate_unique_id())}

    @staticmethod
    def fill_empty_fields(asset: AssetLike):
        """Fill empty fields with their default value."""
        asset_fields_default_value = AssetLike(
            content="",
            json_content="",
            external_id=uuid4().hex,
            json_metadata="{}",
            is_honeypot=False,
            id="",
        )
        field_names = asset_fields_default_value.keys()
        return KiliResolverAsset(
            **{field: asset.get(field, asset_fields_default_value[field]) for field in field_names}
        )

    @staticmethod
    def loop_on_batch(func: Callable[[AssetLike], T]) -> Callable[[List[AssetLike]], List[T]]:
        """Apply a function, that takes a single asset as input, on the whole batch."""

        def loop_func(assets: List[AssetLike]):
            return [func(asset) for asset in assets]

        return loop_func

    @staticmethod
    def build_url_from_parts(*parts) -> str:
        """Builds an url from the parts."""
        return "/".join(parts)

    def _async_import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets with asynchronous resolver."""
        upload_type = "GEO_SATELLITE" if self.input_type == "IMAGE" else "VIDEO"
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
                "uploadType": upload_type,
            },
            "where": {"id": self.project_id},
        }
        result = self.kili.graphql_client.execute(GQL_APPEND_MANY_FRAMES_TO_DATASET, payload)
        format_result("data", result, Asset, self.kili.http_client)
        created_assets_ids = []
        return created_assets_ids

    def _sync_import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets with synchronous resolver."""

        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "isHoneypotArray": [asset["is_honeypot"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
            },
            "where": {"id": self.project_id},
        }
        result = self.kili.graphql_client.execute(GQL_APPEND_MANY_ASSETS, payload)
        created_assets = format_result("data", result, Asset, self.kili.http_client)
        return [asset["id"] for asset in created_assets]

    def import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets to Kili with the right resolver.

        returns:
            created_assets_ids: list of ids of the created assets
        """
        if self.is_asynchronous:
            return self._async_import_to_kili(assets)
        return self._sync_import_to_kili(assets)


class ContentBatchImporter(BaseBatchImporter):
    """Class defining the methods to import a batch of assets with content."""

    def import_batch(self, assets: List[AssetLike], verify: bool):
        """Method to import a batch of asset with content."""
        assets = self.add_ids(assets)
        if not self.is_hosted:
            assets = self.upload_local_content_to_bucket(assets)
        return super().import_batch(assets, verify)

    def get_content_type_and_data_from_content(
        self, content: Optional[Union[str, bytes]]
    ) -> Tuple[bytes, Optional[str]]:
        """Returns the data of the content (path) and its content type."""
        assert content
        assert isinstance(content, str)
        with Path(content).open("rb") as file:
            data = file.read()
            content_type, _ = mimetypes.guess_type(content)
            return data, content_type

    def get_type_and_data_from_content_array(
        self, content_array: List[Optional[Union[str, bytes]]]
    ) -> List[Tuple[Union[bytes, str], Optional[str]]]:
        # pylint:disable=line-too-long
        """Returns the data of the content (path) and its content type for each element in the array."""
        return list(map(self.get_content_type_and_data_from_content, content_array))

    def upload_local_content_to_bucket(self, assets: List[AssetLike]):
        """Upload local content to a bucket."""
        project_bucket_path = self.generate_project_bucket_path()
        asset_content_paths = [
            BaseBatchImporter.build_url_from_parts(
                project_bucket_path, asset.get("id", bucket.generate_unique_id()), "content"
            )
            for asset in assets
        ]
        signed_urls = bucket.request_signed_urls(self.kili, asset_content_paths)
        data_and_content_type_array = self.get_type_and_data_from_content_array(
            list(map(lambda asset: asset.get("content"), assets))
        )
        data_array, content_type_array = zip(*data_and_content_type_array)
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                data_array,
                content_type_array,
                repeat(self.http_client),
            )
        # pylint: disable=line-too-long
        return [AssetLike(**{**asset, "content": url}) for asset, url in zip(assets, url_gen)]  # type: ignore


class JsonContentBatchImporter(BaseBatchImporter):
    """Class defining the import methods for a batch of assets twith json_content."""

    @staticmethod
    def stringify_json_content(asset: AssetLike):
        """Stringify the json content if not a str."""
        json_content = asset.get("json_content", {})
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return AssetLike(**{**asset, "json_content": json_content})  # type: ignore

    def upload_json_content_to_bucket(self, assets: List[AssetLike]):
        """Upload the json_contents to a bucket with signed urls."""
        project_bucket_path = self.generate_project_bucket_path()
        asset_json_content_paths = [
            BaseBatchImporter.build_url_from_parts(
                project_bucket_path,
                asset.get("id", bucket.generate_unique_id()),
                "jsonContent",
            )
            for asset in assets
        ]
        signed_urls = bucket.request_signed_urls(self.kili, asset_json_content_paths)
        json_content_array = [asset.get("json_content") for asset in assets]
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                json_content_array,
                ["text/plain"] * len(assets),
                repeat(self.http_client),
            )
        # pylint: disable=line-too-long
        return [AssetLike(**{**asset, "json_content": url}) for asset, url in zip(assets, url_gen)]  # type: ignore

    def import_batch(self, assets: List[AssetLike], verify: bool):
        """Method to import a batch of asset with json content."""
        assets = self.add_ids(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets = self.upload_json_content_to_bucket(assets)
        return super().import_batch(assets, verify)


class BaseAbstractAssetImporter(abc.ABC):
    """Base class for DataImporters classes."""

    def __init__(
        self,
        kili,
        project_params: ProjectParams,
        processing_params: ProcessingParams,
        logger_params: LoggerParams,
    ):
        self.kili = kili
        self.project_params = project_params
        self.raise_error = processing_params.raise_error
        self.verify = processing_params.verify
        self.pbar = tqdm(disable=logger_params.disable_tqdm)

    @abc.abstractmethod
    def import_assets(self, assets: List[AssetLike]) -> List[str]:
        """Import assets into Kili.

        returns:
            created_assets_ids: list of ids of the created assets
        """
        raise NotImplementedError

    @staticmethod
    def is_hosted_content(assets: List[AssetLike]):
        """Determine if the assets to upload are from local files or hosted data.

        Raise an error if a mix of both.
        """
        contents = [asset.get("content") for asset in assets]
        if all(is_url(content) for content in contents):
            return True
        if any(is_url(content) for content in contents):
            raise ImportValidationError(
                "Cannot upload hosted data and local files at the same time. Please separate the"
                " assets into 2 calls."
            )
        return False

    def _can_upload_from_local_data(self):
        user_me = self.kili.get_user()
        where = OrganizationWhere(
            email=user_me["email"],
        )
        options = QueryOptions(disable_tqdm=True)
        organization = list(
            OrganizationQuery(self.kili.graphql_client, self.kili.http_client)(
                where, ["license.uploadLocalData"], options
            )
        )[0]
        return organization["license"]["uploadLocalData"]

    def _check_upload_is_allowed(self, assets: List[AssetLike]) -> None:
        if not self.is_hosted_content(assets) and not self._can_upload_from_local_data():
            raise UploadFromLocalDataForbiddenError("Cannot upload content from local data")

    def filter_local_assets(self, assets: List[AssetLike], raise_error: bool):
        """Filter out local files that cannot be imported.

        Return an error at the first file that cannot be imported if raise_error is True
        """
        filtered_assets = []
        for asset in assets:
            path = asset.get("content")
            assert path
            assert isinstance(path, str)
            try:
                self.check_mime_type_compatibility(path)
                filtered_assets.append(asset)
            except (FileNotFoundError, MimeTypeError) as err:
                if raise_error:
                    raise err
        if len(filtered_assets) == 0:
            # pylint: disable=line-too-long
            raise ImportValidationError(
                """No files to upload. Check that the paths exist and file types are compatible with the project."""
            )
        return filtered_assets

    def check_mime_type_compatibility(self, path: str):
        """Check that the mimetype of a local file is compatible with the project input type.

        Raise:
             FileNotFoundError: if path do not exists
             MimeTypeError: if the asset is not compatible with the project type
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"file {path} does not exist")
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        input_type = self.project_params.input_type
        if mime_type not in project_compatible_mimetypes[input_type]:
            raise MimeTypeError(
                f"File mime type for {path} is {mime_type} and does not correspond to the type of"
                " the project. File mime type should be one of"
                f" {project_compatible_mimetypes[input_type]}"
            )
        return True

    def filter_duplicate_external_ids(self, assets):
        """Filter out assets whose external_id is already in the project."""
        if len(assets) == 0:
            raise ImportValidationError("No assets to import")
        assets_in_project = AssetQuery(self.kili.graphql_client, self.kili.http_client)(
            AssetWhere(project_id=self.project_params.project_id),
            ["externalId"],
            QueryOptions(disable_tqdm=True),
        )
        external_ids_in_project = [asset["externalId"] for asset in assets_in_project]
        filtered_assets = [
            asset for asset in assets if asset.get("external_id") not in external_ids_in_project
        ]
        if len(filtered_assets) == 0:
            raise ImportValidationError(
                "No assets to import, all given external_ids already exist in the project"
            )
        nb_duplicate_assets = len(assets) - len(filtered_assets)
        if nb_duplicate_assets > 0:
            warnings.warn(
                f"{nb_duplicate_assets} assets were not imported because their external_id are"
                " already in the project",
                stacklevel=2,
            )
        return filtered_assets

    def import_assets_by_batch(
        self,
        assets: List[AssetLike],
        batch_importer: BaseBatchImporter,
        batch_size=IMPORT_BATCH_SIZE,
    ):
        """Split assets by batch and import them with a given batch importer."""
        batch_generator = pagination.BatchIteratorBuilder(assets, batch_size)
        self.pbar.total = len(assets)
        self.pbar.refresh()

        created_asset_ids: List[str] = []
        for i, batch_assets in enumerate(batch_generator):
            # check last batch only
            verify = i == (len(batch_generator) - 1) and self.verify
            created_asset_ids += batch_importer.import_batch(batch_assets, verify)
        return created_asset_ids
