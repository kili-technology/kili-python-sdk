"""
Functions to list plugins
"""
from typing import List

from kili.authentication import KiliAuth
from kili.graphql.operations.plugins.queries import gql_list_plugins
from kili.helpers import format_result, fragment_builder
from kili.types import Plugin


def list_plugins(auth: KiliAuth, fields: List[str]):
    """
    List plugins
    """

    result = auth.client.execute(gql_list_plugins(fragment_builder(fields, Plugin)))
    return format_result("data", result)
