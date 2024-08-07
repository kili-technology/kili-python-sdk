"""GraphQL payload data mappers for api keys operations."""

from kili.domain.project_model import ProjectModelFilters


def project_model_where_mapper(filter: ProjectModelFilters):
    """Build the GraphQL ProjectMapperWhere variable to be sent in an operation."""
    return {
        "projectId": filter.project_id,
        "modelId": filter.model_id,
    }
