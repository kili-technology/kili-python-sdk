"""Helpers for the issue mutations."""


from typing import List

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.exceptions import NotFound


def get_labels_asset_ids_map(kili, project_id: str, label_id_array: List[str]):
    """Return a dictionary that gives for every label id, its associated asset id.

    Returns:
        a dict of key->value: a label id->its associated asset id for the given label ids
    Raises:
        NotFound error if at least one label was not found with its given id
    """
    options = QueryOptions(disable_tqdm=True)
    where = LabelWhere(
        project_id=project_id,
        id_contains=label_id_array,
    )
    labels = list(
        LabelQuery(kili.graphql_client, kili.http_client)(
            where=where, fields=["labelOf.id", "id"], options=options
        )
    )
    labels_not_found = [
        label_id for label_id in label_id_array if label_id not in [label["id"] for label in labels]
    ]
    if len(labels_not_found) > 0:
        raise NotFound(str(labels_not_found))
    return {label["id"]: label["labelOf"]["id"] for label in labels}
