import json
import time
import warnings
from typing import List

import pytest
from tenacity import TryAgain, retry
from tenacity.wait import wait_fixed

from kili.helpers import RetryLongWaitWarner, format_result
from kili.orm import Asset


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
    ret = format_result("data", result, _object=List[Asset])
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
