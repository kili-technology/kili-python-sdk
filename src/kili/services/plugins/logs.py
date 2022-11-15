"""
Functions to get logs of a plugin
"""
from datetime import datetime
from typing import Dict, Optional

from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.queries import GQL_GET_PLUGIN_LOGS
from kili.helpers import format_result


def get_logs(
    auth: KiliAuth,
    plugin: Dict[str, str],
    start_date: Optional[datetime] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
):
    """
    Get logs of a plugin in Kili
    """

    variables = {
        "projectId": plugin["project_id"],
        "pluginName": plugin["plugin_name"],
        "limit": limit,
        "skip": skip,
    }

    if start_date:
        variables["createdAt"] = start_date.isoformat(sep="T", timespec="milliseconds") + "Z"

    result = auth.client.execute(GQL_GET_PLUGIN_LOGS, variables)
    return format_result("data", result)
