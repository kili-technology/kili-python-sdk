import pytest

from kili.client import Kili


@pytest.fixture()
def kili():
    return Kili()


def test_given_orginization_info_when_I_call_create_it_creates_the_organization(kili):
    # Given
    organization_name = "test_organization_python_sdk_e2e"

    # When
    organization_id = kili.internal.create_organization(
        name=organization_name,
        address="1, rue de Rivoli",
        city="Paris",
        country="France",
        zip_code="75001",
    )

    # Then
    organizations = kili.internal.organizations(organization_id=organization_id)
    assert len(organizations) == 1
    assert organizations[0]["name"] == organization_name

    # # Clean
    # kili.internal.delete_organization(organization_id=organization_id)
