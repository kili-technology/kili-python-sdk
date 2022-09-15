import mimetypes
import pathlib
from json import dumps
from typing import List, NamedTuple

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.helpers import format_result, is_url
from kili.orm import Asset
from kili.utils import bucket
from kili.utils.pagination import batch_iterator_builder

from .constants import (
    ASSET_FIELDS_DEFAULT_VALUE,
    IMPORT_BATCH_SIZE,
    mime_extensions_for_IV2,
)
from .exceptions import ImportValidationError, MimeTypeError
from .types import AssetToImport


class BatchParams(NamedTuple):
    """
    Contains all parameters related the batch to import
    """

    is_asynchronous: bool
    is_hosted: bool


class ProjectParams(NamedTuple):
    """
    Contains all parameters related the batch to import
    """

    project_id: str
    input_type: str


class BatchImporter:
    """
    class defining the import of a batch of assets
    """

    def __init__(self, auth: KiliAuth, project_params: ProjectParams, batch_params: BatchParams):
        self.auth = auth
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type
        self.is_hosted = batch_params.is_hosted
        self.is_asynchronous = batch_params.is_asynchronous

    @staticmethod
    def stringify_json_variables(asset):
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
    def fill_empty_fields(asset):
        """
        fill empty fields with their default value
        """
        field_names = ASSET_FIELDS_DEFAULT_VALUE.keys()
        return {
            field: asset.get(field) or ASSET_FIELDS_DEFAULT_VALUE[field] for field in field_names
        }

    def upload_local_contents_to_bucket(self, assets):
        """
        Upload local data to a bucket
        """
        signed_urls = bucket.request_signed_urls(self.auth, self.project_id, len(assets))
        uploaded_assets = []
        for i, asset in enumerate(assets):
            path = asset["content"]
            with open(path, "rb") as file:
                data = file.read()
            content_type, _ = mimetypes.guess_type(path.lower())
            uploaded_content_url = bucket.upload_data_via_rest(signed_urls[i], data, content_type)
            uploaded_assets.append({**asset, "content": uploaded_content_url})
        return uploaded_assets

    def import_to_kili(self, assets):
        """
        Import the processed and uploaded assets into Kili
        """
        request = (
            GQL_APPEND_MANY_FRAMES_TO_DATASET
            if self.is_asynchronous
            else GQL_APPEND_MANY_TO_DATASET
        )
        payload = self.generate_graphql_payload(assets)
        results = self.auth.client.execute(request, payload)
        return format_result("data", results, Asset)

    def generate_graphql_payload(self, assets):
        """
        Generate the payload for graphQL mutation
        """

        if self.is_asynchronous:
            upload_type = "GEOSAT" if self.input_type == "IMAGE" else "VIDEO"
            payload_data = {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
                "uploadType": upload_type,
            }
        else:
            payload_data = {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "isHoneypotArray": [asset["is_honeypot"] for asset in assets],
                "statusArray": [asset["status"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
            }
        return {"data": payload_data, "where": {"id": self.project_id}}

    def import_batch(self, assets: List[AssetToImport]):
        """
        Preprocess the assets, upload them to bucket if necessary and import them into Kili
        """
        if not self.is_hosted:
            assets = self.upload_local_contents_to_bucket(assets)
        asset_batch_to_import = []
        for asset in assets:
            asset = self.stringify_json_variables(asset)
            asset = self.fill_empty_fields(asset)
            asset_batch_to_import.append(asset)
        result_batch = self.import_to_kili(asset_batch_to_import)
        return result_batch


class BaseDataImporter:
    def __init__(
        self,
        auth: KiliAuth,
        project_params: ProjectParams,
    ):
        self.auth = auth
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type

    def is_hosted_data(self, assets):
        """
        Determine if the assets to upload are from local files or hosted data
        Raise an error if a mix of both
        """
        contents = [asset.get("content") for asset in assets]
        if all(is_url(content) for content in contents):
            return True
        elif any(is_url(content) for content in contents):
            raise ImportValidationError(
                """
                Cannot upload hosted data and local files at the same time.
                Please separete the assets into 2 calls
                """
            )

    def run_local_files_checks(self, assets, raise_error=True):
        """
        Filter out local files that cannot be imported.
        Return an error at the first file that cannot be imported if raise_error is True
        """
        filtered_assets = []
        for asset in assets:
            file_exists = self.check_file_exists(asset, raise_error)
            has_right_mime_type = self.check_mime_type_compatibility(asset, raise_error)
            if file_exists and has_right_mime_type:
                filtered_assets.append(asset)
        return filtered_assets

    def check_file_exists(self, asset, raise_error=True):
        """
        Check that the local file exists
        Return an error if it doesn't exist and raise_error is True
        """
        path = pathlib.Path(asset.get("content"))
        file_exists = True
        if not path.is_file():
            file_exists = False
            if raise_error:
                raise FileNotFoundError(f"file {path} does not exist")
        return file_exists

    def check_mime_type_compatibility(self, asset, raise_error=True):
        """
        Check that the mimetype of a local file is compatible with the project input type.
        Return an error if the asset is not compatible and raise_error is True.
        """
        path = pathlib.Path(asset.get("content"))
        mime_type, _ = mimetypes.guess_type(path)
        correct_mime_type = True
        if mime_type is None:
            correct_mime_type = False
            if raise_error:
                raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        if mime_type not in mime_extensions_for_IV2[self.input_type]:
            correct_mime_type = False
            if raise_error:
                raise MimeTypeError(
                    f"""
                    File mime type for {path} is {mime_type} and does not correspond
                    to the type of the project.
                    File mime type should be one of {mime_extensions_for_IV2[self.input_type]}
                    """
                )

        return correct_mime_type

    def import_assets_by_batch(self, assets, batch_importer):
        batch_generator = batch_iterator_builder(assets, IMPORT_BATCH_SIZE)
        for batch_assets in batch_generator:
            response = batch_importer.import_batch(batch_assets)
        return response
