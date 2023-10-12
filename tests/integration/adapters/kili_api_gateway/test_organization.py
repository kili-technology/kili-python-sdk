from kili.adapters.kili_api_gateway.organization.operations_mixin import (
    OrganizationOperationMixin,
)
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
)


def test_create_organization(mocker, graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    organization_name = "test_organization"
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        return_value={
            "data": {
                "id": "fake_organization_id",
                "name": organization_name,
            }
        },
    )

    # When
    organization = kili_api_gateway.create_organization(
        KiliAPIGateWayCreateOrganizationInput(
            name=organization_name,
            address="1, rue de Rivoli",
            city="Paris",
            country="France",
            zip_code="75001",
        ),
        description="Create organization",
        disable_tqdm=False,
    )

    # Then
    assert organization["name"] == organization_name
    print(execute.calls)

    execute.assert_called_with(
        "\nmutation(\n    $data: CreateOrganizationData!\n) {\n  data: createOrganization(\n   "
        " data: $data\n  ) {\n    \nid\n\n  }\n}\n",
        {
            "name": "test_organization",
            "address": "1, rue de Rivoli",
            "city": "Paris",
            "country": "France",
            "zipCode": "75001",
        },
    )
