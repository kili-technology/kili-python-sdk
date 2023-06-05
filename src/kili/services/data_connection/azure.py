"""Code specific to Azure blob storage."""

from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient


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

    def get_blob_paths(self) -> List[str]:
        """List files in the Azure bucket."""
        return list(self.storage_bucket.list_blob_names())

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
    data_integration: Dict, data_connection: Dict
) -> List[str]:
    """Get the blob paths for an Azure data connection using service credentials."""
    azure_client = AzureBucket(
        sas_token=data_integration["azureSASToken"],
        connection_url=data_integration["azureConnectionURL"],
    )

    blob_paths = azure_client.get_blob_paths()

    # blob_paths_in_bucket contains all blob paths in the bucket, we need to filter them
    # to keep only the ones in the data connection selected folders
    if isinstance(data_connection["selectedFolders"], List):
        blob_paths = [
            blob_path
            for blob_path in blob_paths
            if any(
                blob_path.startswith(selected_folder)
                for selected_folder in data_connection["selectedFolders"]
            )
        ]

    return blob_paths
