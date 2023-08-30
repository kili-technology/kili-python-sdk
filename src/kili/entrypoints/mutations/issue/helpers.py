"""Helpers for the issue mutations."""


from typing import Dict, List

import requests

from kili.core.graphql import QueryOptions
from kili.core.graphql.graphql_client import GraphQLClient
from kili.core.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.exceptions import NotFound


def get_labels_asset_ids_map(
    graphql_client: GraphQLClient,
    http_client: requests.Session,
    project_id: str,
    label_id_array: List[str],
) -> Dict:
    """Return a dictionary that gives for every label id, its associated asset id.

    Args:
        graphql_client: instance of the GraphQL client
        http_client: instance of the HTTP client
        project_id: id of the project
        label_id_array: list of label ids

    Returns:
        a dict of key->value a label id->its associated asset id for the given label ids

    Raises:
        NotFound error if at least one label was not found with its given id
    """
    options = QueryOptions(disable_tqdm=True)
    where = LabelWhere(
        project_id=project_id,
        id_contains=label_id_array,
    )
    labels = list(
        LabelQuery(graphql_client, http_client)(
            where=where, fields=["labelOf.id", "id"], options=options
        )
    )
    labels_not_found = [
        label_id for label_id in label_id_array if label_id not in [label["id"] for label in labels]
    ]
    if len(labels_not_found) > 0:
        raise NotFound(str(labels_not_found))
    return {label["id"]: label["labelOf"]["id"] for label in labels}
