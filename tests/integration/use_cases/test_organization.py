from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.organization import OrganizationFilters
from kili.use_cases.organization.use_cases import (
    OrganizationToCreateUseCaseInput,
    OrganizationUseCases,
)


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
        OrganizationToCreateUseCaseInput(
            name=organization_name,
            address="1, rue de Rivoli",
            city="Paris",
            country="France",
            zip_code="75001",
        ),
        disable_tqdm=True,
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
        return_value=[{"id": "fake_organization_id", "name": organization_name}],
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
        "organization_metrics",
        return_value={"nbUsers": 4},
    )

    # When
    organization_use_case = OrganizationUseCases(kili_api_gateway)
    organization_metrics = organization_use_case.organization_metrics()

    # Then
    assert organization_metrics["nbUsers"] == 4


"""
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
    )"""
