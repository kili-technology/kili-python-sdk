"""
GraphQL Queries of Labels
"""


from typing import List, Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.types import Label


class LabelWhere(BaseQueryWhere):
    """
    Tuple to be passed to the LabelQuery to restrict query
    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        category_search: Optional[str] = None,
    ):
        self.project_id = project_id
        self.asset_id = asset_id
        self.asset_status_in = asset_status_in
        self.asset_external_id_in = asset_external_id_in
        self.author_in = author_in
        self.created_at = created_at
        self.created_at_gte = created_at_gte
        self.created_at_lte = created_at_lte
        self.honeypot_mark_gte = honeypot_mark_gte
        self.honeypot_mark_lte = honeypot_mark_lte
        self.id_contains = id_contains
        self.label_id = label_id
        self.type_in = type_in
        self.user_id = user_id
        self.category_search = category_search
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK LabelWhere"""
        return {
            "id": self.label_id,
            "asset": {
                "id": self.asset_id,
                "externalIdStrictlyIn": self.asset_external_id_in,
                "statusIn": self.asset_status_in,
            },
            "project": {
                "id": self.project_id,
            },
            "user": {
                "id": self.user_id,
            },
            "createdAt": self.created_at,
            "createdAtGte": self.created_at_gte,
            "createdAtLte": self.created_at_lte,
            "authorIn": self.author_in,
            "honeypotMarkGte": self.honeypot_mark_gte,
            "honeypotMarkLte": self.honeypot_mark_lte,
            "idIn": self.id_contains,
            "search": self.category_search,
            "typeIn": self.type_in,
        }


class LabelQuery(GraphQLQuery):
    """Label query."""

    TYPE = Label

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL labels query
        """
        return f"""
            query labels($where: LabelWhere!, $first: PageSize!, $skip: Int!) {{
            data: labels(where: $where, first: $first, skip: $skip) {{
                {fragment}
            }}
        }}
        """

    COUNT_QUERY = """
    query countLabels($where: LabelWhere!) {
    data: countLabels(where: $where)
    }
    """
