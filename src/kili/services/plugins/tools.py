"""
Set of common functions used by plugins
"""

from pathlib import Path

DUPLICATE_ERROR_SUBSTRING = "an entity Plugin already exists with value"
DUPLICATE_ACTIVATE_ERROR_SUBSTRING = "an entity Project already exists with value"


def check_errors_plugin_upload(result, plugin_path: Path, plugin_name: str):
    """
    Check if the error during upload is because the plugin already
    exists and print the upload function for the user
    """
    if "errors" in result and DUPLICATE_ERROR_SUBSTRING in result["errors"][0]["message"]:
        print(
            "Hint: A plugin with this name already exist, "
            "if you want to override it you can use the command "
            f'kili.update_plugin(plugin_path="{plugin_path}", plugin_name="{plugin_name}")'
        )


def check_errors_plugin_activation(result, plugin_name: str, project_id: str):
    """
    Check if the error during upload is because the plugin already
    exists and print the upload function for the user
    """
    has_errors = "errors" in result
    if has_errors and DUPLICATE_ACTIVATE_ERROR_SUBSTRING in result["errors"][0]["message"]:
        print(
            f'Warning: A plugin with the name "{plugin_name}" is',
            f'already activated on the project with id "{project_id}"',
        )
        return has_errors, True

    return has_errors, False
