"""
Functions to activate/deactivate a plugin
"""


from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.mutations import (
    GQL_ACTIVATE_PLUGIN_ON_PROJECT,
    GQL_DEACTIVATE_PLUGIN_ON_PROJECT,
)
from kili.helpers import format_result

from .helpers import get_logger


def activate_plugin(auth: KiliAuth, plugin_name: str, project_id: str):
    """
    Create a plugin in Kili
    """

    logger = get_logger()

    variables = {"pluginName": plugin_name, "projectId": project_id}

    result = auth.client.execute(GQL_ACTIVATE_PLUGIN_ON_PROJECT, variables)

    logger.info(f"Plugin {plugin_name} activated on project {project_id}")

    return format_result("data", result)


def deactivate_plugin(auth: KiliAuth, plugin_name: str, project_id: str):
    """
    Create a plugin in Kili
    """

    logger = get_logger()

    variables = {"pluginName": plugin_name, "projectId": project_id}

    result = auth.client.execute(GQL_DEACTIVATE_PLUGIN_ON_PROJECT, variables)

    logger.info(f"Plugin {plugin_name} deactivated on project {project_id}")

    return format_result("data", result)
