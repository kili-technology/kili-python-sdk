"""
Class to upload a plugin
"""

import time
from pathlib import Path
from typing import Optional

from kili.authentication import KiliAuth
from kili.constants import mime_extensions_for_py_scripts
from kili.graphql.operations.plugins.mutations import (
    GQL_CREATE_PLUGIN,
    GQL_CREATE_PLUGIN_RUNNER,
    GQL_GENERATE_UPDATE_URL,
    GQL_UPDATE_PLUGIN_RUNNER,
)
from kili.graphql.operations.plugins.queries import GQL_GET_PLUGIN_RUNNER_STATUS
from kili.helpers import format_result, get_data_type
from kili.services.plugins.tools import check_errors_plugin_upload
from kili.utils import bucket

from .helpers import get_logger

NUMBER_TRIES_RUNNER_STATUS = 20


def check_file_is_py(path: Path, verbose: bool = True) -> bool:
    """
    Returns true if the mime type of the file corresponds to a python file
    """
    mime_type = get_data_type(path.as_posix())

    if not (mime_extensions_for_py_scripts and mime_type):
        return False

    correct_mime_type = mime_type in mime_extensions_for_py_scripts

    if verbose and not correct_mime_type:
        print(
            f"File mime type for {path} is {mime_type} and does not correspond"
            "to the type of the project. "
            f"File mime type should be one of {mime_extensions_for_py_scripts}"
        )
    return correct_mime_type


class PluginUploader:  # pylint: disable=too-few-public-methods
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

    def _retrieve_script(self) -> str:
        """
        Retrieve script from file_path and execute it
        to prevent an upload with indentation errors
        """
        if not check_file_is_py(self.file_path, self.verbose):
            raise ValueError("Wrong file format. ")

        path = Path(self.file_path)

        with path.open("r", encoding="utf-8") as file:
            source_code = file.read()

        return source_code

    def _parse_script(self, source_code: str):
        """
        Method to detect indentation errors in the script
        """
        logger = get_logger()

        # We execute the source code to prevent the upload of a file with SyntaxError
        logger.info(f"Executing {self.file_path.name}...")
        # pylint: disable=exec-used
        exec(source_code, globals())
        logger.info(f"Done executing {self.file_path.name}!")

    @staticmethod
    def _upload_file(source_code: str, url: str):
        """
        Upload a file to a signed url and returns the url with the file_id
        """
        bucket.upload_data_via_rest(url, source_code.encode("utf-8"), "text/x-python")

    def _retrieve_upload_url(self, is_updating_plugin: bool) -> str:
        """
        Retrieve an upload url from the backend
        """
        variables = {"pluginName": self.plugin_name}

        if is_updating_plugin:
            result = self.auth.client.execute(GQL_GENERATE_UPDATE_URL, variables)
        else:
            result = self.auth.client.execute(GQL_CREATE_PLUGIN, variables)

        check_errors_plugin_upload(result, self.file_path, self.plugin_name)
        upload_url = format_result("data", result)
        return upload_url

    def _upload_script(self, is_updating_plugin: bool):
        """
        Upload a script to Kili bucket
        """

        upload_url = self._retrieve_upload_url(is_updating_plugin)

        source_code = self._retrieve_script()
        self._parse_script(source_code)
        self._upload_file(source_code, upload_url)

    def _create_plugin_runner(self):
        """
        Create plugin's runner
        """

        variables = {"pluginName": self.plugin_name}

        result = self.auth.client.execute(GQL_CREATE_PLUGIN_RUNNER, variables)
        return format_result("data", result)

    def _check_plugin_runner_status(self, update=False):
        """
        Check the status of a plugin's runner until it is active
        """

        logger = get_logger()

        action = "updated" if update else "created"

        logger.info(f"Plugin is being {action}... This should take approximately 3 minutes.")

        n_tries = 0
        status = None

        while n_tries < NUMBER_TRIES_RUNNER_STATUS:
            time.sleep(15)

            status = self.get_plugin_runner_status()

            if status == "ACTIVE":
                break

            logger.info(f"Status : {status}...")

            n_tries += 1

        if status == "DEPLOYING" and n_tries == 20:
            raise Exception(
                f"""We could not check your plugin was deployed in time.
Please check again the status of the plugin after some minutes with the command : \
kili.get_plugin_status("{self.plugin_name}").
If the status is different than DEPLOYING or ACTIVE, please check your plugin's code and try to \
overwrite the plugin with a new version of the code (you can use kili.update_plugin() for that)."""
            )

        if status != "ACTIVE":
            raise Exception(
                """There was some error during the creation of the plugin. \
Please check your plugin's code and try to overwrite the plugin with a new version of the \
code (you can use kili.update_plugin() for that)."""
            )

        message = f"Plugin {action} successfully"
        logger.info(message)

        return message

    def get_plugin_runner_status(self):
        """
        Get the status of a plugin's runner
        """

        variables = {"name": self.plugin_name}

        result = self.auth.client.execute(GQL_GET_PLUGIN_RUNNER_STATUS, variables)

        return format_result("data", result)

    def create_plugin(self):
        """
        Create a plugin in Kili
        """

        self._upload_script(False)

        self._create_plugin_runner()

        return self._check_plugin_runner_status()

    def _update_plugin_runner(self):
        """
        Update plugin's runner
        """
        variables = {"pluginName": self.plugin_name}

        result = self.auth.client.execute(GQL_UPDATE_PLUGIN_RUNNER, variables)
        return format_result("data", result)

    def update_plugin(self):
        """
        Update a plugin in Kili
        """

        self._upload_script(True)

        self._update_plugin_runner()

        return self._check_plugin_runner_status(update=True)
