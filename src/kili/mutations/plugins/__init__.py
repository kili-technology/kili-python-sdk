"""Project mutations."""

from pathlib import Path
from typing import Optional

from typeguard import typechecked

from ...authentication import KiliAuth
from ...helpers import Compatible, check_file_is_py, format_result
from .queries import (
    GQL_ACTIVATE_PLUGIN_ON_PROJECT,
    GQL_DEACTIVATE_PLUGIN_ON_PROJECT,
    GQL_UPLOAD_PLUGIN_BETA,
)


class MutationsPlugins:
    """Set of Plugins mutations."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @Compatible(endpoints=["v2"])
    @typechecked
    def upload_plugin_beta(
        self,
        file_path: str,
        plugin_name: Optional[str] = None,
        verbose: bool = True,
    ):
        # pylint: disable=line-too-long
        """Upload a plugin.

        Args:
            project_id: Identifier of the project
            file_path : Path to your .py file
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.upload_plugin_beta(file_path="./path/to/my/file.py")
        """

        if not check_file_is_py(file_path, verbose):
            raise ValueError("Wrong file format. ")

        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            source_code = file.read()

        # We execute the source code to prevent the upload of a file with SyntaxError
        print(f"Executing {path.name}...")
        # pylint: disable=exec-used
        exec(source_code)
        print(f"Done executing {path.name}!")

        if plugin_name is None:
            plugin_name = path.name

        variables = {"pluginName": plugin_name, "pluginSrc": source_code}
        result = self.auth.client.execute(GQL_UPLOAD_PLUGIN_BETA, variables)

        pretty_result = format_result("data", result)
        return pretty_result

    @Compatible(endpoints=["v2"])
    @typechecked
    def activate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.activate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """

        variables = {"pluginName": plugin_name, "projectId": project_id}
        result = self.auth.client.execute(GQL_ACTIVATE_PLUGIN_ON_PROJECT, variables)

        pretty_result = format_result("data", result)
        return pretty_result

    @Compatible(endpoints=["v2"])
    @typechecked
    def deactivate_plugin_on_project(
        self,
        plugin_name: str,
        project_id: str,
    ):
        # pylint: disable=line-too-long
        """Activate a plugin on a project.

        Args:
            plugin_name: Name of the plugin
            project_id: Identifier of the project
            verbose: If false, minimal logs are displayed

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.

        Examples:
            >>> kili.deactivate_plugin_on_project(plugin_name="my_plugin_name", project_id="my_project_id")
        """

        variables = {"pluginName": plugin_name, "projectId": project_id}
        result = self.auth.client.execute(GQL_DEACTIVATE_PLUGIN_ON_PROJECT, variables)

        pretty_result = format_result("data", result)
        return pretty_result
