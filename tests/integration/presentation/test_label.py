from typing import Dict, Generator, List

from typing_extensions import assert_type

from kili.client import Kili
from kili.presentation.client.label import LabelClientMethods
from kili.utils.labels.parsing import ParsedLabel


def test_given_kili_client_when_fetching_labels_then_i_get_correct_type(mocker):
    """This test does not check types at runtime, but rather during pyright type checking."""
    mocker.patch.object(Kili, "__init__")
    mocker.patch.object(LabelClientMethods, "labels")
    assert_type(Kili().labels("project_id"), List[Dict])
    assert_type(Kili().labels("project_id", as_generator=True), Generator[Dict, None, None])
    assert_type(Kili().labels("project_id", output_format="parsed_label"), List[ParsedLabel])
    assert_type(
        Kili().labels("project_id", output_format="parsed_label", as_generator=True),
        Generator[ParsedLabel, None, None],
    )
