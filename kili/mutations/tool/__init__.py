import warnings


def update_tool(client, tool_id: str, project_id: str, json_settings: dict):
    message = """This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
    To update jsonInterface, use:
        playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
    """
    warnings.warn(message, DeprecationWarning)


def append_to_tools(client, project_id: str,  json_settings: dict):
    message = """This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
    To update jsonInterface, use:
        playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
    """
    warnings.warn(message, DeprecationWarning)


def delete_from_tools(client, tool_id: str):
    message = """This function is deprecated. Tools used to describe an interface. They are now called jsonInterface.
    To update jsonInterface, use:
        playground.update_properties_in_project(project_id=project_id, json_interface=json_interface)
    """
    warnings.warn(message, DeprecationWarning)
