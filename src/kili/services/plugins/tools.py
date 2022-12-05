"""
Set of common functions used by plugins
"""

DUPLICATE_ERROR_SUBSTRING = "an entity Plugin already exists with value"


def check_errors_plugin_upload(result, file_path, plugin_name):
    """
    Check if the error during upload is because the plugin already
    exists and print the upload function for the user
    """
    if "errors" in result and DUPLICATE_ERROR_SUBSTRING in result["errors"][0]["message"]:
        print(
            "Hint: A plugin with this name already exist, "
            "if you want to override it you can use the command "
            f'kili.update_plugin(file_path="{file_path}", plugin_name="{plugin_name}")'
        )
