"""
Class to upload a plugin
"""

from pathlib import Path
from typing import Optional

from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.mutations import GQL_UPLOAD_PLUGIN_BETA
from kili.helpers import check_file_is_py, format_result
from kili.utils import bucket


class PluginUploader:
    """
    Class to upload a plugin
    """

    def __init__(
        self, auth: KiliAuth, file_path: str, plugin_name: Optional[str], verbose: bool
    ) -> None:
        self.auth = auth
        self.file_path = Path(file_path)
        self.plugin_name = plugin_name or self.file_path.name
        self.verbose = verbose

    def retrieve_script(self) -> str:
        """
        Retrieve script from file_path and execute it
        to prevent an upload with indentation errors
        """
        if not check_file_is_py(self.file_path, self.verbose):
            raise ValueError("Wrong file format. ")

        path = Path(self.file_path)

        with path.open("r", encoding="utf-8") as file:
            source_code = file.read()

        file.close()

        return source_code

    def parse_script(self, source_code: str):
        """
        Method to detect indentation errors in the script
        """

        # We execute the source code to prevent the upload of a file with SyntaxError
        print(f"Executing {self.file_path.name}...")
        # pylint: disable=exec-used
        exec(source_code)
        print(f"Done executing {self.file_path.name}!")

    def get_signed_upload_url(self) -> str:
        """
        Method to retrieve an upload url
        """
        urls = bucket.request_signed_urls(self.auth, project_id="", size=1)
        return urls[0]

    @staticmethod
    def upload_file(source_code: str, url: str) -> str:
        """
        Upload a file to a signed url and returns the url with the file_id
        """
        url_with_id = bucket.upload_data_via_rest(url, source_code, "text/x-python")
        return url_with_id

    def upload_script(self) -> str:
        """
        Upload a script to Kili bucket
        """

        source_code = self.retrieve_script()
        self.parse_script(source_code)
        upload_url = self.get_signed_upload_url()
        file_url = self.upload_file(source_code, upload_url)
        return file_url

    def create_plugin(self):
        """
        Create a plugin in Kili
        """
        # file_url = self.upload_script()

        plugin_src = self.retrieve_script()

        variables = {"pluginSrc": plugin_src, "pluginName": self.plugin_name}

        result = self.auth.client.execute(GQL_UPLOAD_PLUGIN_BETA, variables)
        return format_result("data", result)
