import copy
import pickle
from concurrent.futures import ProcessPoolExecutor

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout
from urllib3 import HTTPConnectionPool
from urllib3.exceptions import ReadTimeoutError

from kili.exceptions import GraphQLError, MutationOutcomeUnknownError


def _read_timeout() -> ReadTimeout:
    """A read timeout as requests raises it: urllib3 drops its pool when it is pickled."""
    pool = HTTPConnectionPool("127.0.0.1", 4001)
    return ReadTimeout(ReadTimeoutError(pool, "/graphql", "Read timed out. (read timeout=60)"))


def _raise_outcome_unknown(index: int) -> None:
    raise MutationOutcomeUnknownError("appendManyLabels", _read_timeout(), index=index)


@pytest.mark.parametrize(
    "error",
    [
        MutationOutcomeUnknownError("createIssues", _read_timeout()),
        MutationOutcomeUnknownError("appendManyLabels", _read_timeout(), index=200),
        MutationOutcomeUnknownError("appendManyAssets", _read_timeout(), external_ids=["a", "b"]),
    ],
)
def test_mutation_outcome_unknown_error_survives_pickling_and_copying(
    error: MutationOutcomeUnknownError,
):
    for restored in (pickle.loads(pickle.dumps(error)), copy.copy(error)):
        assert isinstance(restored, MutationOutcomeUnknownError)
        assert isinstance(restored, RequestsConnectionError)
        assert str(restored) == str(error)
        assert restored.operation == error.operation
        assert restored.index == error.index
        assert restored.external_ids == error.external_ids
        assert isinstance(restored.cause, ReadTimeout)


def test_mutation_outcome_unknown_error_reaches_the_parent_of_a_process_pool():
    with ProcessPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_raise_outcome_unknown, 100)
        with pytest.raises(MutationOutcomeUnknownError, match="before index 100") as raised:
            future.result(timeout=60)
    assert raised.value.index == 100
    assert "HTTPConnectionPool(host='127.0.0.1', port=4001)" in str(raised.value)


def test_graphql_error_at_an_index_quotes_the_error_like_without_one():
    assert str(GraphQLError("boom")) == 'GraphQL error: "boom"'
    assert str(GraphQLError("boom", index=3)) == 'GraphQL error at index 3: "boom"'
    assert str(GraphQLError("boom", batch_number=2)) == 'GraphQL error at index 200: "boom"'
