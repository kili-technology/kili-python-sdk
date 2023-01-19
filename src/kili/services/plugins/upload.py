"""
Class to upload a plugin
"""

import time
from pathlib import Path
from typing import List, Optional, Union
from zipfile import ZipFile

from kili.authentication import KiliAuth
from kili.constants import mime_extensions_for_py_scripts, mime_extensions_for_txt_files
from kili.graphql.operations.plugins.mutations import (
    GQL_CREATE_PLUGIN,
    GQL_CREATE_PLUGIN_RUNNER,
    GQL_CREATE_WEBHOOK,
    GQL_GENERATE_UPDATE_URL,
    GQL_UPDATE_PLUGIN_RUNNER,
    GQL_UPDATE_WEBHOOK,
)
from kili.graphql.operations.plugins.queries import GQL_GET_PLUGIN_RUNNER_STATUS
from kili.helpers import format_result, get_data_type
from kili.services.plugins.tools import check_errors_plugin_upload
from kili.utils import bucket
from kili.utils.tempfile import TemporaryDirectory

from .helpers import get_logger

NUMBER_TRIES_RUNNER_STATUS = 20


def check_file_mime_type(
    path: Path, compatible_mime_extensions: List[str], verbose: bool = True
) -> bool:
    """
    Returns true if the mime type of the file corresponds to one of compatible_mime_extensions
    """
    mime_type = get_data_type(path.as_posix())

    if not (compatible_mime_extensions and mime_type):
        return False

    correct_mime_type = mime_type in compatible_mime_extensions

    if verbose and not correct_mime_type:
        print(
            f"File mime type for {path} is {mime_type} and does not correspond"
            "to the type of the project. "
            f"File mime type should be one of {compatible_mime_extensions}"
        )
    return correct_mime_type


def check_file_is_py(path: Path, verbose: bool = True) -> bool:
    """
    Returns true if the mime type of the file corresponds to a python file
    """
    return check_file_mime_type(path, mime_extensions_for_py_scripts, verbose)


def check_file_is_txt(path: Path, verbose: bool = True) -> bool:
    """
    Returns true if the mime type of the file corresponds to a .txt file
    """
    return check_file_mime_type(path, mime_extensions_for_txt_files, verbose)


class WebhookUploader:
    """
    Class to create a webhook
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        auth: KiliAuth,
        webhook_url: str,
        plugin_name: str,
        header: Optional[str],
        verbose: bool,
    ) -> None:
        self.auth = auth
        self.webhook_url = webhook_url
        self.plugin_name = plugin_name or self.webhook_url
        self.header = header
        self.verbose = verbose

    def create_webhook(self):
        """
        Create a webhook receiving Kili events
        """

        variables = {
            "pluginName": self.plugin_name,
            "webhookUrl": self.webhook_url,
            "header": self.header,
        }

        result = self.auth.client.execute(GQL_CREATE_WEBHOOK, variables)

        return format_result("data", result)

    def update_webhook(self):
        """
        Update a webhook receiving Kili events
        """

        variables = {
            "pluginName": self.plugin_name,
            "webhookUrl": self.webhook_url,
            "header": self.header,
        }

        result = self.auth.client.execute(GQL_UPDATE_WEBHOOK, variables)

        return format_result("data", result)


class PluginUploader:
    """
    Class to upload a plugin
    """

    def __init__(
        self, auth: KiliAuth, plugin_path: str, plugin_name: Optional[str], verbose: bool
    ) -> None:
        self.auth = auth
        self.plugin_path = Path(plugin_path)

        if (not self.plugin_path.is_dir()) and (not self.plugin_path.is_file()):
            raise FileNotFoundError(
                f"""The provided path "{plugin_path}" is neither a directory nor a file.
                The absolute path is the following: '{self.plugin_path.absolute()}'"""
            )

        if plugin_name:
            self.plugin_name = plugin_name
        else:
            self.plugin_name = self.plugin_path.name
        self.verbose = verbose

    def _retrieve_plugin_src(self) -> List[Path]:
        """
        Retrieve script from plugin_path and execute it
        to prevent an upload with indentation errors
        """

        if self.plugin_path.is_dir():

            file_path = self.plugin_path / "main.py"
            if not file_path.is_file():
                raise FileNotFoundError(
                    f"No main.py file in the provided folder: {self.plugin_path.absolute()}"
                )

            file_paths = list(self.plugin_path.glob("**/*.py"))

            return file_paths

        file_path = self.plugin_path

        if not check_file_is_py(file_path, self.verbose):
            raise ValueError("Wrong file format.")

        return [file_path]

    def _retrieve_requirements(self) -> Union[Path, None]:
        """
        Retrieve script from file_path and execute it
        to prevent an upload with indentation errors
        """

        if not self.plugin_path.is_dir():
            return None

        file_path = self.plugin_path / "requirements.txt"
        if not file_path.is_file():
            logger = get_logger()
            logger.info(
                f"No requirements.txt file in the provided folder: {self.plugin_path.absolute()}"
            )
            return None

        if not check_file_is_txt(file_path, self.verbose):
            raise ValueError("Wrong file format.")

        return file_path

    @staticmethod
    def _parse_script(file_path: Path):
        """
        Method to detect indentation errors in the script
        """
        with file_path.open("r", encoding="utf-8") as file:
            source_code = file.read()

        # We execute the source code to prevent the upload of a file with SyntaxError
        compile(source_code, "<string>", "exec")

    @staticmethod
    def _upload_file(zip_path: Path, url: str):
        """
        Upload a file to a signed url and returns the url with the file_id
        """
        bucket.upload_data_via_rest(url, zip_path.read_bytes(), "application/zip")

    def _retrieve_upload_url(self, is_updating_plugin: bool) -> str:
        """
        Retrieve an upload url from the backend
        """
        variables = {"pluginName": self.plugin_name}

        if is_updating_plugin:
            result = self.auth.client.execute(GQL_GENERATE_UPDATE_URL, variables)
        else:
            result = self.auth.client.execute(GQL_CREATE_PLUGIN, variables)

        check_errors_plugin_upload(result, self.plugin_path, self.plugin_name)
        upload_url = format_result("data", result)
        return upload_url

    def _create_zip(
        self, file_paths: List[Path], requirements_path: Optional[Path], tmp_directory: Path
    ):
        """
        Create a zip file from python file and requirements.txt
        (if user has defined a path to a requirements.txt)
        """
        zip_path = tmp_directory / "archive.zip"

        with ZipFile(zip_path, "w") as archive:

            if len(file_paths) == 1:
                archive.write(file_paths[0], "main.py")

            else:
                for path in file_paths:
                    archive.write(path, path.relative_to(self.plugin_path))

            if requirements_path:
                archive.write(requirements_path, requirements_path.relative_to(self.plugin_path))

        return zip_path

    def _upload_script(self, is_updating_plugin: bool):
        """
        Upload a script to Kili bucket
        """

        upload_url = self._retrieve_upload_url(is_updating_plugin)

        file_paths = self._retrieve_plugin_src()

        for path in file_paths:
            self._parse_script(path)

        requirements = self._retrieve_requirements()

        with TemporaryDirectory() as tmp_directory:

            zip_path = self._create_zip(file_paths, requirements, tmp_directory)

            self._upload_file(zip_path, upload_url)

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

            if status in ("ACTIVE", "FAILED"):
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
