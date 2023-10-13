import pytest

from kili.client import Kili


@pytest.fixture()
def kili():
    return Kili()


@pytest.mark.skip(
    "Skipping this test, because there is no way to remove an organization. To be run manually"
    " only."
)
def test_given_orginization_info_when_I_call_create_it_creates_the_organization(kili: Kili):
    # Given
    organization_name = "test_organization_python_sdk_e2e"

    # When
    organization = kili.internal.create_organization(
        name=organization_name,
        address="1, rue de Rivoli",
        city="Paris",
        country="France",
        zip_code="75001",
    )

    # Then
    organizations = kili.organizations(organization_id=organization["id"])
    assert len(organizations) == 1
    assert organizations[0]["name"] == organization_name


def test_given_stored_organizations_when_I_call_organizations_it_lists_them(kili: Kili):
    # Given: it is assumed there are organinations in the database

    # When
    organizations = kili.organizations(as_generator=False, first=10)

    # Then
    assert "name" in organizations[0]


def test_given_stored_organizations_when_I_call_count_organizations_it_counts_them(kili: Kili):
    # Given: it is assumed there are organinations in the database

    # When
    organization_count = kili.count_organizations()

    # Then
    assert organization_count > 0


def test_given_stored_organization_when_I_call_organization_metrics_it_retrives_them(kili: Kili):
    # Given
    organization = kili.organizations(as_generator=False, first=1)[0]

    # When
    organization_metrics = kili.organization_metrics(organization_id=organization["id"])

    # Then
    assert "numberOfAnnotations" in organization_metrics
    assert "numberOfHours" in organization_metrics
    assert "numberOfLabeledAssets" in organization_metrics
