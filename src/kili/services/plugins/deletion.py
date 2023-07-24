"""Function to delete a plugin."""

from kili.core.graphql.operations.plugin.mutations import GQL_DELETE_PLUGIN
from kili.core.helpers import format_result

from .helpers import get_logger


def delete_plugin(kili, plugin_name: str) -> str:
    """Create a plugin in Kili."""
    logger = get_logger()

    variables = {"pluginName": plugin_name}

    result = kili.graphql_client.execute(GQL_DELETE_PLUGIN, variables)

    logger.info(f"Plugin {plugin_name} deleted!")

    return format_result("data", result, None, kili.http_client)
