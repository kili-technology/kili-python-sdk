"""GraphQL payload data mappers for api keys operations."""

from kili.domain.api_key import ApiKeyFilters


def api_key_where_mapper(filters: ApiKeyFilters):
    """Build the GraphQL ApiKeyWhere variable to be sent in an operation."""
    return {
        "user": {"id": filters.user_id},
        "id": filters.api_key_id,
        "key": filters.api_key,
    }
