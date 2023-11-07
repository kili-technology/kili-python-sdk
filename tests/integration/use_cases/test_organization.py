from datetime import datetime

import pytz

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
)
from kili.use_cases.organization.use_cases import OrganizationUseCases


def test_given_orginization_info_when_I_call_create_use_case_it_creates_the_organization(
    graphql_client, http_client, mocker
):
    # Given
    organization_name = "test_organization"
    kili_api_gateway = KiliAPIGateway(graphql_client, http_client)
    mocker.patch.object(
        kili_api_gateway,
        "create_organization",
        return_value={"id": "fake_organization_id", "name": organization_name},
    )

    # When
    organization_use_case = OrganizationUseCases(kili_api_gateway)
    organization = organization_use_case.create_organization(
        OrganizationToCreateInput(
            name=organization_name,
            address="1, rue de Rivoli",
            city="Paris",
            country="France",
            zip_code="75001",
        ),
    )

    # Then
    assert organization["name"] == organization_name


def test_given_existing_organization_when_I_call_list_organisations_then_it_lists_it(
    graphql_client, http_client, mocker
):
    # Given
    kili_api_gateway = KiliAPIGateway(graphql_client, http_client)
    organization_name = "test_organization"
    mocker.patch.object(
        kili_api_gateway,
        "list_organizations",
        return_value=(o for o in [{"id": "fake_organization_id", "name": organization_name}]),
    )

    # When
    organization_use_case = OrganizationUseCases(kili_api_gateway)
    organizations = organization_use_case.list_organizations(
        where=OrganizationFilters(), fields=["id", "name"], options=QueryOptions(disable_tqdm=True)
    )

    # Then
    assert next(organizations)["name"] == organization_name


def test_given_existing_organization_when_I_call_count_organisations_then_it_counts_them(
    graphql_client, http_client, mocker
):
    # Given
    kili_api_gateway = KiliAPIGateway(graphql_client, http_client)
    mocker.patch.object(
        kili_api_gateway,
        "count_organizations",
        return_value=4,
    )

    # When
    organization_use_case = OrganizationUseCases(kili_api_gateway)
    organization_count = organization_use_case.count_organizations(where=OrganizationFilters())

    # Then
    assert organization_count == 4


def test_given_existing_organization_when_I_call_organization_metrics_the_it_retrieves_them(
    graphql_client, http_client, mocker
):
    # Given
    kili_api_gateway = KiliAPIGateway(graphql_client, http_client)
    mocker.patch.object(
        kili_api_gateway,
        "get_organization_metrics",
        return_value={"nbUsers": 4},
    )

    # When
    organization_use_cases = OrganizationUseCases(kili_api_gateway)
    organization_metrics = organization_use_cases.get_organization_metrics(
        OrganizationMetricsFilters(
            id=OrganizationId("fake_organization_id"),
            start_datetime=datetime.now(tz=pytz.UTC),
            end_datetime=datetime.now(tz=pytz.UTC),
        ),
        fields=["nbUsers"],
    )

    # Then
    assert organization_metrics["nbUsers"] == 4


def test_given_a_stored_organization_when_i_call_update_properties_in_organization_it_updates_it(
    graphql_client, http_client, mocker
):
    # Given
    kili_api_gateway = KiliAPIGateway(graphql_client, http_client)
    mocker.patch.object(
        kili_api_gateway,
        "update_organization",
        return_value={"id": "fake_organization_id", "name": "new_name"},
    )

    # When
    organization_use_cases = OrganizationUseCases(kili_api_gateway)
    organization = organization_use_cases.update_organization(
        organization_id=OrganizationId("fake_organization_id"),
        organization_data=OrganizationToUpdateInput(name="new_name", license={}),
    )

    # Then
    assert organization["name"] == "new_name"
