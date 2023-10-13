from datetime import datetime

import pytest
import pytz
from pytest_mock import MockerFixture

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.client import Kili
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
)
from kili.use_cases.organization.use_cases import OrganizationUseCases


@pytest.fixture()
def kili():
    return Kili()


def test_given_orginization_info_when_I_call_create_it_creates_the_organization(
    kili: Kili, mocker: MockerFixture
):
    # Given
    organization_name = "test_organization"
    mocker.patch.object(
        OrganizationUseCases,
        "create_organization",
        return_value={"id": "fake_organization_id", "name": organization_name},
    )

    # When
    organization = kili.internal.create_organization(
        name=organization_name,
        address="1, rue de Rivoli",
        city="Paris",
        country="France",
        zip_code="75001",
    )

    # Then
    assert organization["name"] == organization_name


def test_given_organization_in_kili_when_I_call_organizations_it_lists_the_organization(
    kili: Kili, mocker: MockerFixture
):
    # Given
    organization_name = "test_organization"
    list_organization_use_case = mocker.patch.object(
        OrganizationUseCases,
        "list_organizations",
        return_value=[{"id": "fake_organization_id", "name": organization_name}],
    )

    # When
    organizations = kili.organizations(
        organization_id="fake_organization_id",
        fields=["id", "name", "license"],
        skip=0,
        first=200,
        disable_tqdm=True,
    )

    # Then
    assert organizations[0]["name"] == organization_name
    list_organization_use_case.assert_called_with(
        OrganizationFilters(email=None, organization_id=OrganizationId("fake_organization_id")),
        ["id", "name", "license"],
        QueryOptions(disable_tqdm=True, first=200, skip=0),
    )


def test_given_organization_in_kili_when_I_call_count_organizations_it_counts_the_organizations(
    kili: Kili, mocker: MockerFixture
):
    # Given
    count_organizations_use_case = mocker.patch.object(
        OrganizationUseCases,
        "count_organizations",
        return_value=5,
    )

    # When
    organization_count = kili.count_organizations(email="jean.philippe@kili-technology.com")

    # Then
    assert organization_count == 5
    count_organizations_use_case.assert_called_with(
        OrganizationFilters(email="jean.philippe@kili-technology.com", organization_id=None)
    )


def test_given_organization_in_kili_when_I_call_organization_metrics_it_retrieves_them(
    kili: Kili, mocker: MockerFixture
):
    # Given
    organization_id = "fake_organization_id"
    metrics = {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}
    get_organizations_metrics_use_case = mocker.patch.object(
        OrganizationUseCases,
        "get_organization_metrics",
        return_value=metrics,
    )

    # When
    organization_metrics = kili.organization_metrics(
        organization_id=organization_id,
        start_date=datetime(2022, 1, 1, tzinfo=pytz.UTC),
        end_date=datetime(2022, 1, 5, tzinfo=pytz.UTC),
    )

    # Then
    assert organization_metrics == metrics
    get_organizations_metrics_use_case.assert_called_with(
        OrganizationMetricsFilters(
            id=OrganizationId(organization_id),
            start_datetime=datetime(2022, 1, 1, tzinfo=pytz.UTC),
            end_datetime=datetime(2022, 1, 5, tzinfo=pytz.UTC),
        )
    )


def test_given_organization_in_kili_when_I_call_update_properties_in_organization_it_updates_them(
    kili: Kili, mocker: MockerFixture
):
    # Given
    test_organization_id = "fake_organization_id"
    new_name = "new_name_{}".format(datetime.now(tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"))
    update_properties_in_organization_use_case = mocker.patch.object(
        OrganizationUseCases,
        "update_properties_in_organization",
        return_value={"id": test_organization_id, "name": new_name},
    )

    # When
    result = kili.internal.update_properties_in_organization(
        organization_id=test_organization_id, name=new_name
    )

    # Then
    update_properties_in_organization_use_case.assert_called_with(
        organization_id=test_organization_id, name=new_name
    )
    assert result["name"] == new_name
