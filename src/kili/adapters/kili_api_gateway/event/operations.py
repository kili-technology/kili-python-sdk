"""GraphQL Event operations."""


def get_events_query(fragment: str) -> str:
    """Return the GraphQL events query."""
    return f"""
          query Events($where: EventsWhere!, $pagination: EventPagination!, $order: Order) {{
            data: events(where: $where, pagination: $pagination, order: $order) {{
                {fragment}
              }}
            }}
        """
