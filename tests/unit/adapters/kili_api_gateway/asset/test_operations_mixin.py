"""Tests for the createUploadBucketSignedUrls dispatch in the asset operations mixin."""

from graphql import OperationDefinitionNode, OperationType, parse

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway

# A recent backend serves createUploadBucketSignedUrls from both root types: the query is kept and
# deprecated, the mutation is the one to use. Exposing it on both here is what makes this schema
# faithful to a deployed backend; a mutation-only schema would describe a state that never exists.
# The query-only case below is the one that fails if the dispatch is ever switched to detecting the
# backend by the presence of the query field.
SCHEMA_WITH_QUERY_AND_MUTATION = """
type Query {
  createUploadBucketSignedUrls(filePaths: [String!]): [String!]
}

type Mutation {
  createUploadBucketSignedUrls(filePaths: [String!]): [String!]
}
"""

SCHEMA_WITH_QUERY_ONLY = """
type Query {
  createUploadBucketSignedUrls(filePaths: [String!]): [String!]
}
"""

FILE_PATHS = ["projects/fake_proj_id/assets/fake_file.png"]


def _operation_type_of(document: str) -> OperationType:
    definition = parse(document).definitions[0]
    assert isinstance(definition, OperationDefinitionNode)
    return definition.operation


def test_given_backend_exposing_the_mutation_when_i_request_signed_urls_then_it_sends_a_mutation(
    make_graphql_client, http_client, mocker
):
    # Given
    graphql_client = make_graphql_client(SCHEMA_WITH_QUERY_AND_MUTATION)
    execute = mocker.patch.object(
        graphql_client, "execute", return_value={"urls": ["https://fake_signed_url"]}
    )
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    urls = gateway.create_upload_bucket_signed_urls(FILE_PATHS)

    # Then
    document, payload = execute.call_args.args
    assert _operation_type_of(document) is OperationType.MUTATION
    assert payload == {"filePaths": FILE_PATHS}
    assert urls == ["https://fake_signed_url"]


def test_given_backend_without_the_mutation_when_i_request_signed_urls_then_it_sends_a_query(
    make_graphql_client, http_client, mocker
):
    # Given a backend that predates the mutation
    graphql_client = make_graphql_client(SCHEMA_WITH_QUERY_ONLY)
    execute = mocker.patch.object(
        graphql_client, "execute", return_value={"urls": ["https://fake_signed_url"]}
    )
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    urls = gateway.create_upload_bucket_signed_urls(FILE_PATHS)

    # Then
    document, payload = execute.call_args.args
    assert _operation_type_of(document) is OperationType.QUERY
    assert payload == {"filePaths": FILE_PATHS}
    assert urls == ["https://fake_signed_url"]


def test_given_no_local_schema_when_i_request_signed_urls_then_it_sends_a_mutation(
    make_graphql_client, http_client, mocker
):
    # Given a client with no local schema, as with KILI_SDK_SKIP_CHECKS
    graphql_client = make_graphql_client(None)
    execute = mocker.patch.object(
        graphql_client, "execute", return_value={"urls": ["https://fake_signed_url"]}
    )
    gateway = KiliAPIGateway(graphql_client, http_client)

    # When
    gateway.create_upload_bucket_signed_urls(FILE_PATHS)

    # Then the backend, not the SDK, decides whether the mutation exists
    document, _ = execute.call_args.args
    assert _operation_type_of(document) is OperationType.MUTATION
