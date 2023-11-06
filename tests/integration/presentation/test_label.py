from typing import Dict, Generator, List

import pytest
import pytest_mock
from typing_extensions import assert_type

from kili.adapters.kili_api_gateway.mixin import KiliAPIGateway
from kili.client import Kili
from kili.domain.project import ProjectId
from kili.presentation.client.label import LabelClientMethods
from kili.use_cases.label import LabelUseCases
from kili.utils.labels.parsing import ParsedLabel


def test_given_kili_client_when_fetching_labels_then_i_get_correct_type(mocker):
    """This test does not check types at runtime, but rather during pyright type checking."""
    mocker.patch.object(Kili, "__init__", return_value=None)
    mocker.patch.object(LabelClientMethods, "labels")
    assert_type(Kili().labels("project_id"), List[Dict])
    assert_type(Kili().labels("project_id", as_generator=True), Generator[Dict, None, None])
    assert_type(Kili().labels("project_id", output_format="parsed_label"), List[ParsedLabel])
    assert_type(
        Kili().labels("project_id", output_format="parsed_label", as_generator=True),
        Generator[ParsedLabel, None, None],
    )


def test_given_kili_client_when_fetching_prediction_labels_then_it_calls_proper_use_case(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    mocked_use_cases = mocker.patch.object(LabelUseCases, "list_labels")

    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    _ = kili.predictions("fake_proj_id")

    # Then
    assert mocked_use_cases.call_count == 1


def test_given_kili_client_when_fetching_inference_labels_then_it_calls_proper_use_case(
    mocker: pytest_mock.MockerFixture, kili_api_gateway: KiliAPIGateway
):
    mocked_use_cases = mocker.patch.object(LabelUseCases, "list_labels")

    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    _ = kili.inferences("fake_proj_id")

    # Then
    assert mocked_use_cases.call_count == 1


def test_given_kili_client_when_adding_labels_with_mixed_ids_then_it_crashes(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When Then
    with pytest.raises(
        ValueError,
        match="Either provide asset IDs or asset external IDs. Not both at the same time.",
    ):
        _ = kili.append_labels(
            asset_id_array=["asset_id_1", "asset_id_2"],
            asset_external_id_array=["asset_external_id_1", "asset_external_id_2"],
            json_response_array=[{}, {}],
        )


def test_given_kili_client_when_adding_predictions_without_model_name_then_it_crashes(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When Then
    with pytest.raises(
        ValueError,
        match="You must provide `model_name` when uploading `PREDICTION` labels.",
    ):
        _ = kili.append_labels(
            asset_id_array=["asset_id_1", "asset_id_2"],
            asset_external_id_array=None,
            label_type="PREDICTION",
            json_response_array=[{}, {}],
        )


def test_given_kili_client_when_creating_honeypot_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    mocker.patch.object(
        LabelUseCases, "create_honeypot_label", return_value={"id": "honeypot_label_id"}
    )

    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    label = kili.create_honeypot(asset_id="asset_id", json_response={})

    # Then
    assert label == {"id": "honeypot_label_id"}


def test_given_kili_client_when_counting_labels_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    mocker.patch.object(LabelUseCases, "count_labels", return_value=42)

    # Given
    kili = LabelClientMethods()
    kili.kili_api_gateway = kili_api_gateway

    # When
    nb_label = kili.count_labels(project_id=ProjectId("project_id"))

    # Then
    assert nb_label == 42
