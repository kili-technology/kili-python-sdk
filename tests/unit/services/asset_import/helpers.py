import os
import uuid

from kili.adapters.http_client import HttpClient


class LocalDownloader:
    def __init__(self, directory, http_client: HttpClient) -> None:
        self.directory = directory
        self.http_client = http_client

    def __call__(self, url):
        content = self.http_client.get(url)
        name = os.path.basename(url)
        path = os.path.join(self.directory, f"{uuid.uuid4()}-{name}")
        with open(path, "wb") as file:
            file.write(content.content)
        return path
