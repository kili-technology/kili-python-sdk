"""The step filters given by id reach the queries, and keep their positional neutrality."""

import pytest
import pytest_mock

from kili.presentation.client.asset import AssetClientMethods
from kili.presentation.client.label import LabelClientMethods

V3_STEPS = ([{"id": "label-1", "name": "Label"}, {"id": "label-2", "name": "Label"}], "V3")


@pytest.fixture()
def assets_client(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "kili.presentation.client.asset.ProjectUseCases.get_project_steps_and_version",
        return_value=V3_STEPS,
    )
    count = mocker.patch(
        "kili.presentation.client.asset.AssetUseCases.count_assets", return_value=0
    )
    kili = AssetClientMethods()
    kili.kili_api_gateway = mocker.MagicMock()
    return kili, count


def test_count_assets_sends_the_step_ids_given(assets_client):
    kili, count = assets_client

    kili.count_assets(
        "project",
        step_id_in=["label-2"],
        step_id_and_status_not_in=[("label-1", "DONE")],
    )

    filters = count.call_args.args[0]
    assert filters.step_id_in == ["label-2"]
    assert filters.step_id_and_status_not_in == [("label-1", "DONE")]


def test_count_assets_refuses_a_step_filter_given_by_id_and_by_name(assets_client):
    kili, _ = assets_client

    with pytest.raises(ValueError, match="both given"):
        kili.count_assets("project", step_id_in=["label-2"], step_name_in=["Label"])


def test_count_assets_refuses_a_step_id_filter_with_status_in(assets_client):
    kili, _ = assets_client

    with pytest.raises(ValueError, match="step id and status_in"):
        kili.count_assets("project", step_id_in=["label-2"], status_in=["TODO"])


def test_count_labels_sends_the_asset_step_ids_given(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "kili.presentation.client.label.ProjectUseCases.get_project_steps_and_version",
        return_value=V3_STEPS,
    )
    count = mocker.patch(
        "kili.presentation.client.label.LabelUseCases.count_labels", return_value=0
    )
    kili = LabelClientMethods()
    kili.kili_api_gateway = mocker.MagicMock()

    kili.count_labels("project", asset_step_id_in=["label-2"])

    assert count.call_args.kwargs["filters"].asset.step_id_in == ["label-2"]
