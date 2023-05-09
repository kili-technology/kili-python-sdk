"""Code specific to Azure blob storage."""

from typing import Tuple
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient, ContainerClient


class AzureBucket:
    def __init__(self, sas_token: str, connection_url: str) -> None:
        self.sas_token = sas_token
        self.connection_url = connection_url

        self.storage_account, self.container_name = self.get_storage_account_and_container_name(
            connection_url
        )
        self.blob_sas_url = f"https://{self.storage_account}.blob.core.windows.net?{self.sas_token}"
        self.client = BlobServiceClient(account_url=self.blob_sas_url)
        self.storage_bucket = self.client.get_container_client(self.container_name)

    @staticmethod
    def get_storage_account_and_container_name(connection_url: str) -> Tuple[str, str]:
        SPLIT_VALUE = ".blob.core.windows.net"
        url_connection = urlparse(connection_url)
        storage_account = url_connection.hostname.split(SPLIT_VALUE)[0]
        container_name = url_connection.path.lstrip("/")
        return storage_account, container_name

    def check_connection(self):
        iterator = self.storage_bucket.list_blobs()

        try:
            next(iterator)
        except Exception as err:
            raise ValueError(
                "Unable to connect to the Azure bucket. Please check your credentials."
            ) from err
        else:
            return
