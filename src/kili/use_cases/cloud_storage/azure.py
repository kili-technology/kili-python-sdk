"""Code specific to Azure blob storage."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient

from kili.domain.project import InputType


class AzureBucket:
    """Class for Azure blob storage buckets."""

    def __init__(self, sas_token: str, connection_url: str) -> None:
        """Initialize the Azure bucket."""
        self.sas_token = sas_token
        self.connection_url = connection_url

        self.storage_account, self.container_name = (
            self._split_connection_url_into_storage_account_and_container_name(connection_url)
        )
        self.blob_sas_url = f"https://{self.storage_account}.blob.core.windows.net?{self.sas_token}"
        self.client = BlobServiceClient(account_url=self.blob_sas_url)
        self.storage_bucket = self.client.get_container_client(self.container_name)

    @staticmethod
    def _split_connection_url_into_storage_account_and_container_name(
        connection_url: str,
    ) -> Tuple[str, str]:
        """Split the connection url into storage account and container name."""
        split_value = ".blob.core.windows.net"
        url_connection = urlparse(connection_url)
        storage_account = url_connection.hostname.split(split_value)[0]  # type: ignore
        container_name = url_connection.path.lstrip("/")
        return storage_account, container_name

    def get_blob_paths_as_tree(self) -> Dict:
        """Get a tree representation of the Azure bucket.

        Folder structure is represented as a dictionary.
        A folder is represented as a key with a value as a dictionary.
        A file is represented as a key with a value as None.
        """
        filetree = {}

        for filepath in self.storage_bucket.list_blob_names():
            current_node = filetree
            *folders, filename = Path(filepath).parts
            for folder in folders:
                if folder not in current_node:
                    current_node[folder] = {}
                current_node = current_node[folder]
            if filename:
                current_node[filename] = None

        return filetree

    def get_blob_paths_azure_data_connection_with_service_credentials(
        self, selected_folders: Optional[List[str]], input_type: InputType
    ) -> Tuple[List[str], List[Optional[str]]]:
        """Get the blob paths for an Azure data connection using service credentials."""
        blob_paths = []
        warnings = set()
        for blob in self.storage_bucket.list_blobs():
            if not hasattr(blob, "name") or not isinstance(blob.name, str):
                continue

            # blob_paths_in_bucket contains all blob paths in the bucket, we need to filter them
            # to keep only the ones in the data connection selected folders
            if isinstance(selected_folders, List) and not any(
                blob.name.startswith(selected_folder) for selected_folder in selected_folders
            ):
                continue

            has_content_type_field = (
                hasattr(blob, "content_settings")
                and hasattr(blob.content_settings, "content_type")
                and isinstance(blob.content_settings.content_type, str)
            )
            if not has_content_type_field:
                warnings.add("Objects with missing content-type were ignored")

            elif not self._is_content_type_compatible_with_input_type(
                blob.content_settings.content_type,  # pyright: ignore[reportGeneralTypeIssues]
                input_type,
            ):
                warnings.add(
                    "Objects with unsupported content-type for this type of project were ignored"
                )

            else:
                blob_paths.append(blob.name)

        return blob_paths, list(warnings)

    @staticmethod
    def _is_content_type_compatible_with_input_type(
        content_type: str, input_type: InputType
    ) -> bool:
        """Check if the content type is compatible with the input type."""
        if input_type == "IMAGE":
            return content_type.startswith("image")

        if input_type == "VIDEO":
            return content_type.startswith("video")

        if input_type == "PDF":
            return content_type.startswith("application/pdf")

        if input_type == "TEXT":
            return any(
                content_type.startswith(text_type)
                for text_type in (
                    "application/json",
                    "text/plain",
                    "text/html",
                    "text/csv",
                    "text/xml",
                )
            )

        raise ValueError(f"Unknown project input type: {input_type}")
