from typing import Dict, List

import pytest

from kili.use_cases.cloud_storage.azure import AzureBucket


@pytest.mark.parametrize(
    ("blob_names", "expected_tree"),
    [
        (
            ["bears/bear-01.png", "bears/bear-02.jpg", "bears/bear-03.jpg"],
            {"bears": {"bear-01.png": None, "bear-02.jpg": None, "bear-03.jpg": None}},
        ),
        (
            ["bears/subfold1/bear-01.png", "bears/bear-02.jpg", "bears/bear-03.jpg"],
            {
                "bears": {
                    "subfold1": {"bear-01.png": None},
                    "bear-02.jpg": None,
                    "bear-03.jpg": None,
                }
            },
        ),
        (
            [
                "bears/subfold1/bear-01.png",
                "bears/sub1/sub2/bear-02.jpg",
                "bear-03.jpg",
                "bears/sub4/truc.txt",
            ],
            {
                "bears": {
                    "subfold1": {"bear-01.png": None},
                    "sub1": {"sub2": {"bear-02.jpg": None}},
                    "sub4": {"truc.txt": None},
                },
                "bear-03.jpg": None,
            },
        ),
        (
            ["file4.txt", "folderA/file1.txt", "folderA/file2.txt", "folderA/folderB/file3.txt"],
            {
                "folderA": {"folderB": {"file3.txt": None}, "file2.txt": None, "file1.txt": None},
                "file4.txt": None,
            },
        ),
    ],
)
def test_azure_get_tree(mocker, blob_names: List[str], expected_tree: Dict):
    mocker.patch.object(AzureBucket, "__init__", return_value=None)
    azure_client = AzureBucket(sas_token="", connection_url="")
    azure_client.storage_bucket = mocker.MagicMock(
        list_blob_names=mocker.MagicMock(return_value=blob_names)
    )

    tree = azure_client.get_blob_paths_as_tree()
    assert tree == expected_tree
