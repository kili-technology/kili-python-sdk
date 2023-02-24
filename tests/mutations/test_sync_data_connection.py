from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from kili.mutations.data_connection import MutationsDataConnection


class MockerGetDataConnection:
    """
    Class to mock the get_data_connection function
    """

    def __init__(
        self, added: int, removed: int, total: int, nb_of_assets: int, is_checking: bool
    ) -> None:
        self.added = added
        self.removed = removed
        self.total = total
        self.nb_of_assets = nb_of_assets
        self.is_checking = is_checking

    def __call__(self, auth, data_connection_id: str, fields: List[str]) -> Dict[str, Any]:
        ret = {"id": data_connection_id}
        ret["dataDifferencesSummary"] = {}

        if "dataDifferencesSummary.added" in fields:
            ret["dataDifferencesSummary"]["added"] = self.added
        if "dataDifferencesSummary.removed" in fields:
            ret["dataDifferencesSummary"]["removed"] = self.removed
        if "dataDifferencesSummary.total" in fields:
            ret["dataDifferencesSummary"]["total"] = self.total
        if "isChecking" in fields:
            ret["isChecking"] = self.is_checking
        if "numberOfAssets" in fields:
            ret["numberOfAssets"] = self.nb_of_assets

        return ret


@patch("kili.graphql.GraphQLClient")
@patch("kili.services.data_connection.validate_data_differences")
@patch("kili.services.data_connection.get_data_connection")
@pytest.mark.parametrize(
    "delete_extraneous_files,data_connection_ret_values,log_messages",
    [
        (
            False,
            {"added": 0, "removed": 0, "total": 0, "nb_of_assets": 100, "is_checking": False},
            (
                "Found 100 asset(s) in the data connection.",
                "No differences found. Nothing to synchronize.",
            ),
        ),
        (
            False,
            {"added": 0, "removed": 12, "total": 42, "nb_of_assets": 50, "is_checking": False},
            (
                "Found 50 asset(s) in the data connection.",
                "Found 42 difference(s)",
                "Use delete_extraneous_files=True to remove 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {"added": 0, "removed": 12, "total": 42, "nb_of_assets": 50, "is_checking": False},
            (
                "Found 50 asset(s) in the data connection.",
                "Found 42 difference(s)",
                "Removed 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {"added": 444, "removed": 1, "total": 1000, "nb_of_assets": 2000, "is_checking": False},
            (
                "Found 2000 asset(s) in the data connection.",
                "Found 1000 difference(s)",
                "Removed 1 extraneous file(s).",
                "Added 444 file(s).",
            ),
        ),
    ],
)
def test_synchronize_data_connection(
    mocked_get_data_connection,
    mocked_validate_data_differences,
    mocked_graphql_client,
    delete_extraneous_files,
    data_connection_ret_values,
    log_messages,
    caplog,
) -> None:
    """
    Test synchronize_data_connection mutation
    """

    class BackendSubscriptionEventGenerator:
        """
        Simulates a backend subscription event generator
        """

        def __init__(self, *args, **_) -> None:
            assert "subscription dataConnectionUpdated($projectID: ID!)" in args[0]
            assert "data: dataConnectionUpdated(projectID: $projectID)" in args[0]
            assert "isChecking" in args[0]

            assert args[1] == {"projectID": "my_project_id"}

        def __iter__(self):
            return self

        def __next__(self):
            return {"data": {"isChecking": False}}

    kili = MutationsDataConnection(auth=MagicMock(client=mocked_graphql_client))
    mocked_graphql_client.subscribe = MagicMock(side_effect=BackendSubscriptionEventGenerator)
    mocked_get_data_connection.side_effect = MockerGetDataConnection(**data_connection_ret_values)

    kili.synchronize_data_connection(
        project_id="my_project_id",
        data_connection_id="my_data_connection_id",
        delete_extraneous_files=delete_extraneous_files,
    )

    assert "Synchronizing data connection: my_data_connection_id" in caplog.text
    for log_msg in log_messages:
        assert log_msg in caplog.text

    if delete_extraneous_files and data_connection_ret_values["removed"] > 0:
        mocked_validate_data_differences.assert_any_call(
            kili.auth,
            "REMOVE",
            "my_data_connection_id",
        )

    if data_connection_ret_values["added"] > 0:
        mocked_validate_data_differences.assert_any_call(
            kili.auth,
            "ADD",
            "my_data_connection_id",
        )
