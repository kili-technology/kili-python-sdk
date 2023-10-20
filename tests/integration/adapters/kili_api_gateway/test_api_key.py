from kili.adapters.kili_api_gateway.api_key.operations_mixin import ApiKeyOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.api_key import ApiKeyFilters


def test_given_filters_and_fields_when_i_call_list_api_keys_it_returns_them(graphql_client):
    # Given
    kili_api_gateway = ApiKeyOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    graphql_client.execute.side_effect = [
        {"data": 1},  # response to count query
        {  # response to list query
            "data": [
                {
                    "key": "hello",
                }
            ]
        },
    ]
    filters = ApiKeyFilters()
    fields = ["key"]
    options = QueryOptions(skip=0, first=1, disable_tqdm=True)

    # When
    api_keys = kili_api_gateway.list_api_keys(
        filters=filters,
        fields=fields,
        options=options,
    )

    # Then
    assert next(api_keys)["key"] == "hello"
    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\n        query apiKeys($where: ApiKeyWhere!, $first: PageSize!, $skip: Int!) {\n     "
        "     data: apiKeys(where: $where, skip: $skip, first: $first) {\n             key\n   "
        "       }\n        }\n        ",
        {"where": {"user": {"id": None}, "id": None, "key": None}, "skip": 0, "first": 1},
    )
