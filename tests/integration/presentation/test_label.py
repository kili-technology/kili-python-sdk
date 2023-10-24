from typing import Dict, Generator, List

import pytest_mock
from typing_extensions import assert_type

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
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
