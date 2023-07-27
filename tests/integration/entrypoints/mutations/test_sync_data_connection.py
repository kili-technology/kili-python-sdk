from typing import Any, Dict, List, Optional

import pytest

from kili.entrypoints.mutations.data_connection import MutationsDataConnection


class MockerGetDataConnection:
    """Class to mock the get_data_connection function."""

    def __init__(
        self,
        added: int,
        removed: int,
        total: int,
        nb_of_assets: int,
        is_checking: bool,
        project_id: str,
        selected_folders: Optional[List[str]],
        data_integration: Dict = {
            "azureIsUsingServiceCredentials": False,
            "platform": "AWS",
            "azureSASToken": "fake_token",
            "azureConnectionURL": "fake_url",
            "id": "fake_data_integration_id",
        },
    ) -> None:
        self.added = added
        self.removed = removed
        self.total = total
        self.nb_of_assets = nb_of_assets
        self.is_checking = is_checking
        self.project_id = project_id
        self.selected_folders = selected_folders
        self.data_integration = data_integration

    def __call__(self, auth, data_connection_id: str, fields: List[str]) -> Dict[str, Any]:
        ret: Dict[str, Any] = {"id": data_connection_id}

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
        if "projectId" in fields:
            ret["projectId"] = self.project_id
        if "selectedFolders" in fields:
            ret["selectedFolders"] = self.selected_folders
        if any(field.startswith("dataIntegration.") for field in fields):
            ret["dataIntegration"] = self.data_integration

        return ret


@pytest.mark.parametrize(
    "delete_extraneous_files,data_connection_ret_values,log_messages",
    [
        (
            False,
            {
                "added": 0,
                "removed": 0,
                "total": 0,
                "nb_of_assets": 100,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 100 asset(s) imported from the data connection.",
                "No differences found. Nothing to synchronize.",
            ),
        ),
        (
            False,
            {
                "added": 0,
                "removed": 12,
                "total": 42,
                "nb_of_assets": 50,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 50 asset(s) imported from the data connection.",
                "Found 42 difference(s)",
                "Use delete_extraneous_files=True to remove 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {
                "added": 0,
                "removed": 12,
                "total": 42,
                "nb_of_assets": 50,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 50 asset(s) imported from the data connection.",
                "Found 42 difference(s)",
                "Removed 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {
                "added": 444,
                "removed": 1,
                "total": 1000,
                "nb_of_assets": 2000,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 2000 asset(s) imported from the data connection.",
                "Found 1000 difference(s)",
                "Removed 1 extraneous file(s).",
                "Added 444 file(s).",
            ),
        ),
    ],
)
def test_synchronize_cloud_storage_connection(
    delete_extraneous_files,
    data_connection_ret_values,
    log_messages,
    caplog,
    mocker,
) -> None:
    """Test synchronize_cloud_storage_connection mutation."""
    mocked_trigger_validate_data_differences = mocker.patch(
        "kili.services.data_connection.trigger_validate_data_differences"
    )
    mocked_get_data_connection = mocker.patch("kili.services.data_connection.get_data_connection")
    mocked_get_data_connection.side_effect = MockerGetDataConnection(**data_connection_ret_values)
    mocker.patch("kili.services.data_connection.Retrying", return_value=[])

    kili = MutationsDataConnection()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    kili.synchronize_cloud_storage_connection(
        cloud_storage_connection_id="my_data_connection_id",
        delete_extraneous_files=delete_extraneous_files,
    )

    assert "Synchronizing data connection: my_data_connection_id" in caplog.text
    for log_msg in log_messages:
        assert log_msg in caplog.text

    if delete_extraneous_files and data_connection_ret_values["removed"] > 0:
        mocked_trigger_validate_data_differences.assert_any_call(
            kili,
            "REMOVE",
            "my_data_connection_id",
        )

    if data_connection_ret_values["added"] > 0:
        mocked_trigger_validate_data_differences.assert_any_call(
            kili,
            "ADD",
            "my_data_connection_id",
        )
