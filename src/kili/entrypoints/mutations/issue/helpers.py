"""Helpers for the issue mutations."""


from typing import Dict, List

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.exceptions import NotFound


def get_labels_asset_ids_map(
    kili_api_gateway: KiliAPIGateway,
    project_id: str,
    label_id_array: List[str],
) -> Dict:
    """Return a dictionary that gives for every label id, its associated asset id.

    Args:
        kili_api_gateway: instance of KiliAPIGateway
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
        LabelQuery(kili_api_gateway.graphql_client, kili_api_gateway.http_client)(
            where=where, fields=["labelOf.id", "id"], options=options
        )
    )
    labels_not_found = [
        label_id for label_id in label_id_array if label_id not in [label["id"] for label in labels]
    ]
    if len(labels_not_found) > 0:
        raise NotFound(str(labels_not_found))
    return {label["id"]: label["labelOf"]["id"] for label in labels}
