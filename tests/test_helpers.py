import json
from typing import List

import pytest

from kili.exceptions import GraphQLError
from kili.helpers import format_result
from kili.orm import Asset


@pytest.mark.parametrize(
    "result",
    [
        r'{"errors": {"message": "NetworkError when attempting to fetch resource.", "stack": ""}}',
        r"""
        {
          "errors": [
            {
              "message": "Syntax Error: Expected Name, found \":\".",
              "locations": [
                {
                  "line": 5,
                  "column": 10
                }
              ],
              "extensions": {
                "code": "GRAPHQL_PARSE_FAILED"
              }
            }
          ]
        }
        """,
        r"""
        {
          "errors": [
            {
              "message": "Field \"emaiel\" is not defined by type \"UserWhere\". Did you mean \"email\"?",
              "locations": [
                {
                  "line": 2,
                  "column": 31
                }
              ],
              "extensions": {
                "code": "GRAPHQL_VALIDATION_FAILED"
              }
            }
          ]
        }
        """,
        r"""
        {
          "errors": [
            {
              "message": "Bad type of input PageSize, expected type integer, got type object.",
              "extensions": {
                "code": "GRAPHQL_VALIDATION_FAILED"
              }
            },
            {
              "message": "Field \"projects\" argument \"where\" of type \"ProjectWhere!\" is required, but it was not provided.",
              "locations": [
                {
                  "line": 2,
                  "column": 3
                }
              ],
              "extensions": {
                "code": "GRAPHQL_VALIDATION_FAILED"
              }
            }
          ]
        }
        """,
        (
            r'{"errors":[{"message":"[accessDenied] Access denied. Please verify your credentials'
            r" or contact Kili support. -- This can be due to: The data you are trying to mutate"
            r" does not exist or is not accessible | trace :"
            r' false","locations":[{"line":8,"column":3}],"path":["data"],"extensions":{"code":"401"}}],"data":{"data":null}}'
        ),
    ],
)
def test_format_result_error(result):
    with pytest.raises(GraphQLError):
        result = json.loads(result)
        format_result(name="data", result=result)


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
