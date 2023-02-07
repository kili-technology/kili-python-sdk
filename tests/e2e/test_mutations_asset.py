import pytest

from kili.client import Kili


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def src_project(kili):
    interface = {
        "jobs": {
            "DETECTION": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "instruction": "Is there a defect ? Where ? What kind ?",
                "required": 0,
                "isChild": False,
                "content": {
                    "categories": {
                        "DEFECT_CLASS_1": {"name": "defect of class 1"},
                        "DEFECT_CLASS_2": {"name": "defect of class 2"},
                        "DEFECT_CLASS_3": {"name": "defect of class 3"},
                        "DEFECT_CLASS_4": {"name": "defect of class 4"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_mutations_asset",
        description="test_mutations_asset",
    )

    kili.append_many_to_dataset(
        project_id=project["id"],
        content_array=[
            "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
            "https://storage.googleapis.com/label-public-staging/car/car_2.jpg",
            "https://storage.googleapis.com/label-public-staging/car/car_2.jpg",
        ],
        external_id_array=["1", "2", "3"],
    )
    assets = kili.assets(project_id=project["id"], fields=["externalId", "id"])
    asset_id_array = [x["id"] for x in assets]

    json_response = {
        "DETECTION": {
            "annotations": [
                {
                    "boundingPoly": [
                        {
                            "normalizedVertices": [
                                {"x": 0.4344363401082048, "y": 0.4371570074066614},
                                {"x": 0.4344363401082048, "y": 0.2517629644814394},
                                {"x": 0.6601656139293334, "y": 0.2517629644814394},
                                {"x": 0.6601656139293334, "y": 0.4371570074066614},
                            ]
                        }
                    ],
                    "categories": [{"name": "DEFECT_CLASS_1"}],
                    "mid": "20221228110616573-6974",
                    "type": "rectangle",
                    "children": {},
                }
            ]
        }
    }

    kili.append_labels(
        asset_id_array,
        json_response_array=[json_response, json_response, json_response],
    )

    yield project

    kili.delete_project(project["id"])


def test_delete_many_from_dataset(kili, src_project):
    assets = kili.assets(src_project["id"], fields=["id"])
    asset_ids = [asset["id"] for asset in assets]
    ret = kili.delete_many_from_dataset(asset_ids=asset_ids[:2])

    assert ret["id"] == src_project["id"]

    assets = kili.assets(src_project["id"], fields=["id"])
    assert assets[0]["id"] == asset_ids[2]


def test_add_to_review(kili, src_project):
    assets = kili.assets(src_project["id"], fields=["id"])
    asset_ids = [asset["id"] for asset in assets]
    ret = kili.add_to_review(asset_ids=asset_ids[:2])  # send two assets to review

    assert ret["id"] == src_project["id"]
    assert sorted(ret["asset_ids"]) == sorted(asset_ids[:2])


def test_send_back_to_queue(kili, src_project):
    assets = kili.assets(src_project["id"], fields=["id"])
    asset_ids = [asset["id"] for asset in assets]
    kili.add_to_review(asset_ids=asset_ids)  # send all assets to review
    ret = kili.send_back_to_queue(asset_ids[:2])  # two assets back to queue

    assert ret["id"] == src_project["id"]
    assert sorted(ret["asset_ids"]) == sorted(asset_ids[:2])


def test_change_asset_external_ids(kili, src_project):
    assets = kili.assets(src_project["id"], fields=["id"])
    asset_ids = [asset["id"] for asset in assets]
    ret = kili.change_asset_external_ids(asset_ids=asset_ids[:2], new_external_ids=["111", "222"])

    assert len(ret) == 2
    assert sorted([asset["id"] for asset in ret]) == sorted(asset_ids[:2])

    assets = kili.assets(src_project["id"], fields=["externalId"])
    assert sorted([asset["externalId"] for asset in assets]) == ["111", "222", "3"]


def test_update_properties_in_assets_errors(kili):
    with pytest.raises(ValueError):
        kili.update_properties_in_assets(asset_ids=None, external_ids=None)

    with pytest.raises(ValueError):
        kili.update_properties_in_assets(asset_ids=["1"], external_ids=["1"])

    with pytest.raises(ValueError):
        kili.update_properties_in_assets(asset_ids=None, external_ids=["1"], project_id=None)


def test_update_properties_in_assets_external_id(kili, src_project):
    assets = kili.assets(src_project["id"], fields=["id", "externalId"])

    ret = kili.update_properties_in_assets(
        external_ids=[asset["externalId"] for asset in assets],
        priorities=[1, 0, 0],
        project_id=src_project["id"],
    )
    assert len(ret) == 3

    assets_new = kili.assets(src_project["id"], fields=["id", "externalId", "priority"])

    assert [asset["externalId"] for asset in assets_new] == ["1", "2", "3"]
    assert [asset["priority"] for asset in assets_new] == [1, 0, 0]
