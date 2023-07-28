import pytest_mock

from kili.entrypoints.mutations.label import GQL_DELETE_LABELS, MutationsLabel


def test_delete_labels(mocker: pytest_mock.MockerFixture):
    kili = MutationsLabel()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    kili.delete_labels(ids=["id1", "id2"])

    kili.graphql_client.execute.assert_called_once_with(
        GQL_DELETE_LABELS,
        {"ids": ["id1", "id2"]},
    )


def test_delete_labels_big_batch(mocker: pytest_mock.MockerFixture):
    kili = MutationsLabel()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    kili.delete_labels(ids=["id1"] * 101)

    assert kili.graphql_client.execute.call_count == 2
