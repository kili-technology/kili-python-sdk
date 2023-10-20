# def map_update_organization_data(organization_data: OrganizationToUpdateInput) -> Dict:
#     """Build the GraphQL OrganizationData variable to be sent in an operation."""
#     license_str = None if not organization_data.license else json.dumps(organization_data.license)
#     data = {}
#     if organization_data.name is not None:
#         data["name"] = organization_data.name
#     if license_str is not None:
#         data["license"] = license_str
#     return data

import pytest

from kili.adapters.kili_api_gateway.organization.mappers import (
    map_update_organization_data,
)
from kili.domain.organization import OrganizationToUpdateInput


@pytest.mark.parametrize(
    ("organization_data", "expected"),
    [
        (
            OrganizationToUpdateInput(name="name", license={"license_field": "license_value"}),
            {"name": "name", "license": '{"license_field": "license_value"}'},
        ),
        (OrganizationToUpdateInput(name="name", license=None), {"name": "name"}),
        (
            OrganizationToUpdateInput(name=None, license={"license_field": "license_value"}),
            {"license": '{"license_field": "license_value"}'},
        ),
    ],
)
def test_map_update_organization_data(organization_data, expected):
    assert map_update_organization_data(organization_data) == expected
