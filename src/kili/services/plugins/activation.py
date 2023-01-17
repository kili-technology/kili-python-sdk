"""
Functions to activate/deactivate a plugin
"""


from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.mutations import (
    GQL_ACTIVATE_PLUGIN_ON_PROJECT,
    GQL_DEACTIVATE_PLUGIN_ON_PROJECT,
)
from kili.helpers import format_result
from kili.services.plugins.helpers import get_logger
from kili.services.plugins.tools import check_errors_plugin_activation


def activate_plugin(auth: KiliAuth, plugin_name: str, project_id: str):
    """
    Create a plugin in Kili
    """

    logger = get_logger()

    variables = {"pluginName": plugin_name, "projectId": project_id}

    result = auth.client.execute(GQL_ACTIVATE_PLUGIN_ON_PROJECT, variables)

    has_failed, already_activated = check_errors_plugin_activation(result, plugin_name, project_id)

    if not already_activated and not has_failed:
        logger.info(f'Plugin with name "{plugin_name}" activated on project "{project_id}"')

    return format_result("data", result) if not already_activated else None


def deactivate_plugin(auth: KiliAuth, plugin_name: str, project_id: str):
    """
    Create a plugin in Kili
    """

    logger = get_logger()

    variables = {"pluginName": plugin_name, "projectId": project_id}

    result = auth.client.execute(GQL_DEACTIVATE_PLUGIN_ON_PROJECT, variables)

    logger.info(f"Plugin {plugin_name} deactivated on project {project_id}")

    return format_result("data", result)
