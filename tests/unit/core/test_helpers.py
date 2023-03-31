import json
import time
import warnings
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from tenacity import TryAgain, retry
from tenacity.wait import wait_fixed

from kili.core.helpers import RetryLongWaitWarner, format_result
from kili.exceptions import MissingArgumentError
from kili.graphql.operations.label.queries import LabelQuery
from kili.mutations.asset import MutationsAsset
from kili.mutations.issue.helpers import get_labels_asset_ids_map
from kili.orm import Asset
from tests.fakes.fake_kili import FakeAuth


def test_format_result_no_type_conversion_1():
    result = r'{"data":{"id":"claqu1f012345678905oi4evp","email":"username@kili-technology.com"}}'
    result = json.loads(result)
    ret = format_result("data", result)
    assert ret == {"id": "claqu1f012345678905oi4evp", "email": "username@kili-technology.com"}


def test_format_result_no_type_conversion_2():
    result = r'{"data":[{"createdAt":"2022-12-12T13:52:14.989Z"},{"createdAt":"2022-12-09T08:33:55.940Z"},{"createdAt":"2022-11-29T16:48:09.456Z"},{"createdAt":"2022-11-29T16:44:29.652Z"},{"createdAt":"2022-11-29T16:44:06.341Z"},{"createdAt":"2022-11-29T16:40:07.941Z"},{"createdAt":"2022-11-25T08:14:12.298Z"}]}'
    result = json.loads(result)
    ret = format_result("data", result)
    assert len(ret) == 7
    assert all("createdAt" in x for x in ret)


def test_format_result_formatted_json_is_list():
    result = {
        "data": [
            {
                "labels": [
                    {
                        "author": {
                            "id": "claqu1frp1xc90loh05oi4evp",
                            "email": "josdfsdfn@kili-technology.com",
                        },
                        "createdAt": "2022-12-15T12:15:53.344Z",
                        "id": "clbp1p0x1234567s6epuca1ry",
                        "jsonResponse": '{"JOB_0":{"categories":[{"name":"OBJECT_A"}]}}',
                    }
                ],
                "content": "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                "createdAt": "2022-12-15T12:15:52.169Z",
                "externalId": "car_1",
                "id": "clbp1oz123456789zcl9l85ci",
                "isHoneypot": False,
                "jsonMetadata": "{}",
                "skipped": False,
                "status": "TODO",
            }
        ]
    }
    ret = format_result("data", result, object_=List[Asset])
    assert isinstance(ret, list)
    assert isinstance(ret[0], Asset)


def test_format_result_legacy_orm_objects():
    result = r'{"data":[{"id": "clbp1ozzb12345678cl9l85ci"}]}'
    result = json.loads(result)
    ret = format_result("data", result, Asset)
    assert len(ret) == 1
    assert isinstance(ret, list)
    assert isinstance(ret[0], Asset)


def test_format_result_with_type_conversion_int():
    result = r'{"data":400}'
    result = json.loads(result)
    ret = format_result("data", result, int)
    assert isinstance(ret, int)


def test_retry_long_wait_warner():
    class MyTestClass:
        def __init__(self):
            self.start_time = None

        @retry(
            wait=wait_fixed(0.05),
            before_sleep=RetryLongWaitWarner(
                warn_after=0.25,
                logger_func=warnings.warn,
                warn_message="warn_message_defined_by_user",
            ),
        )
        def my_method_takes_some_time(self):
            self.start_time = self.start_time or time.time()
            if time.time() - self.start_time < 0.5:
                raise TryAgain("Try again")
            return

    with pytest.warns(match="warn_message_defined_by_user"):
        MyTestClass().my_method_takes_some_time()


def test_get_labels_asset_ids_map():
    with patch.object(
        LabelQuery,
        "__call__",
        return_value=iter(
            [
                {"id": "label_id_1", "labelOf": {"id": "asset_id_1"}},
                {"id": "label_id_2", "labelOf": {"id": "asset_id_1"}},
            ]
        ),
    ):
        assert get_labels_asset_ids_map(
            FakeAuth, "project_id", ["label_id_1", "label_id_2"]  # type: ignore
        ) == {
            "label_id_1": "asset_id_1",
            "label_id_2": "asset_id_1",
        }


@patch("kili.mutations.asset._mutate_from_paginated_call", return_value=[{"data": None}])
class TestCheckWarnEmptyList(TestCase):
    """Tests for the check_warn_empty_list helper."""

    def test_kwargs_empty(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with pytest.warns(
            UserWarning,
            match=(
                "Method 'add_to_review' did nothing because the following argument is empty:"
                " asset_ids."
            ),
        ):
            ret = kili.add_to_review(asset_ids=[], external_ids=[])
        assert ret is None
        mocked__mutate_from_paginated_call.assert_not_called()

    def test_args_empty(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with pytest.warns(
            UserWarning,
            match=(
                "Method 'add_to_review' did nothing because the following argument is empty:"
                " asset_ids."
            ),
        ):
            ret = kili.add_to_review([], [])
        assert ret is None
        mocked__mutate_from_paginated_call.assert_not_called()

    def test_none(self, mocked__mutate_from_paginated_call):
        """Test that the helper does not raise a warning if args are None."""
        kili = MutationsAsset(auth=MagicMock())
        with pytest.raises(MissingArgumentError):
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                kili.add_to_review()
        mocked__mutate_from_paginated_call.assert_not_called()

    def test_kwargs_one_empty(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with pytest.warns(
            UserWarning,
            match=(
                "Method 'add_to_review' did nothing because the following argument is empty:"
                " external_ids."
            ),
        ):
            ret = kili.add_to_review(asset_ids=None, external_ids=[], project_id="project_id")
        assert ret is None
        mocked__mutate_from_paginated_call.assert_not_called()

    def test_kwargs_one_empty_2(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with pytest.warns(
            UserWarning,
            match=(
                "Method 'add_to_review' did nothing because the following argument is empty:"
                " asset_ids"
            ),
        ):
            ret = kili.add_to_review(asset_ids=[], external_ids=None)
        assert ret is None
        mocked__mutate_from_paginated_call.assert_not_called()

    def test_kwargs_no_warning_correct_input(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            kili.add_to_review(asset_ids=["asset_id"], external_ids=None)
        mocked__mutate_from_paginated_call.assert_called_once()

    def test_args_no_warning_correct_input(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            kili.add_to_review(["asset_id"], None)
        mocked__mutate_from_paginated_call.assert_called_once()

    def test_warn_change_asset_external_ids(self, mocked__mutate_from_paginated_call):
        kili = MutationsAsset(auth=MagicMock())
        with pytest.warns(
            UserWarning,
            match=(
                "Method 'change_asset_external_ids' did nothing because the following argument is"
                " empty: new_external_ids"
            ),
        ):
            ret = kili.change_asset_external_ids(new_external_ids=[], asset_ids=[])
        assert ret == []
        mocked__mutate_from_paginated_call.assert_not_called()
