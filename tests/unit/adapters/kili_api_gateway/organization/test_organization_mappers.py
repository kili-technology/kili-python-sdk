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
