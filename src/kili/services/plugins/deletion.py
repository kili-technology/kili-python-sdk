"""
Function to delete a plugin
"""
from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.mutations import GQL_DELETE_PLUGIN
from kili.helpers import format_result


def delete_plugin(auth: KiliAuth, plugin_name: str):
    """
    Create a plugin in Kili
    """

    variables = {"pluginName": plugin_name}

    result = auth.client.execute(GQL_DELETE_PLUGIN, variables)
    return format_result("data", result)
