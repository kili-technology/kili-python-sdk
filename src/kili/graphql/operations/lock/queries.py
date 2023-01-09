"""
GraphQL Queries of Locks
"""

from typing import Optional

from kili.graphql import BaseQueryWhere, GraphQLQuery
from kili.types import Lock


class LockWhere(BaseQueryWhere):
    """
    Tuple to be passed to the LockQuery to restrict query
    """

    # pylint: disable=too-many-arguments,too-many-locals,too-many-instance-attributes

    def __init__(
        self,
        lock_id: Optional[str] = None,
    ):
        self.lock_id = lock_id
        super().__init__()

    def graphql_where_builder(self):
        """Build the GraphQL Where payload sent in the resolver from the SDK LockWhere"""
        return {"id": self.lock_id}


class LockQuery(GraphQLQuery):
    """Lock query."""

    TYPE = Lock

    @staticmethod
    def query(fragment):
        """
        Return the GraphQL locks query
        """
        return f"""
    query locks($where: LockWhere!, $first: PageSize!, $skip: Int!) {{
    data: locks(where: $where, first: $first, skip: $skip) {{
        {fragment}
    }}
    }}
    """

    COUNT_QUERY = """
    query countLocks($where: LockWhere!) {
    data: countLocks(where: $where)
    }
    """
