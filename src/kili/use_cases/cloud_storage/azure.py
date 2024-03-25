"""Code specific to Azure blob storage."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient

from kili.domain.project import InputType


def get_blob_paths_azure_data_connection_with_service_credentials(
    data_connection: Dict, data_integration: Dict, input_type: InputType
) -> Tuple[List[str], List[str], List[str]]:
    """Get the blob paths for an Azure data connection using service credentials."""
    if not (data_integration["azureSASToken"] and data_integration["azureConnectionURL"]):
        raise ValueError(
            f"Cannot retrieve blob paths for data connection {data_connection['id']} with data"
            f" integration {data_integration['id']}. Need to provide \"azureSASToken\" and"
            f' "azureConnectionURL" in data integration: {data_integration}'
        )

    return AzureBucket(
        sas_token=data_integration["azureSASToken"],
        connection_url=data_integration["azureConnectionURL"],
    ).get_blob_paths_azure_data_connection_with_service_credentials(
        input_type=input_type,
        selected_folders=data_connection.get("selectedFolders"),
        prefix=data_connection.get("prefix"),
        include=data_connection.get("include"),
        exclude=data_connection.get("exclude"),
    )


class AzureBucket:
    """Class for Azure blob storage buckets."""

    def __init__(self, sas_token: str, connection_url: str) -> None:
        """Initialize the Azure bucket."""
        self.sas_token = sas_token
        self.connection_url = connection_url

        (
            self.storage_account,
            self.container_name,
        ) = self._split_connection_url_into_storage_account_and_container_name(connection_url)
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
        # pylint: disable=line-too-long
        storage_account = url_connection.hostname.split(  # pyright: ignore[reportOptionalMemberAccess]
            split_value
        )[0]
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

    @staticmethod
    def _generate_regex_pattern(pattern: str) -> str:
        pattern = re.escape(pattern)

        if "*" in pattern:
            pattern = pattern.replace(r"\*", ".+")
            pattern = f"^{pattern}$"
        else:
            pattern = f"^{pattern}"

        return pattern

    def get_blob_paths_azure_data_connection_with_service_credentials(
        self,
        input_type: InputType,
        selected_folders: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> Tuple[List[str], List[str], List[str]]:
        """Get the blob paths for an Azure data connection using service credentials."""
        blob_paths = []
        content_types = []
        warnings = set()
        include = [self._generate_regex_pattern(pattern) for pattern in include] if include else []
        exclude = [self._generate_regex_pattern(pattern) for pattern in exclude] if exclude else []
        for blob in self.storage_bucket.list_blobs(name_starts_with=prefix):
            if not hasattr(blob, "name") or not isinstance(blob.name, str):
                continue

            if (
                prefix is None
                and isinstance(selected_folders, List)
                and not any(
                    blob.name.startswith(selected_folder) for selected_folder in selected_folders
                )
            ):
                continue

            if len(include) > 0 and not any(re.match(pattern, blob.name) for pattern in include):
                continue

            if len(exclude) > 0 and any(re.match(pattern, blob.name) for pattern in exclude):
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
                content_types.append(blob.content_settings.content_type)

        return blob_paths, list(warnings), content_types

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
