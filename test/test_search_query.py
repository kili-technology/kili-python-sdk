"""Tests for category search validation"""

import pytest

from kili.helpers import validate_category_search_query

TEST_CASES = [
    {
        "case": "user does not provide job",
        "query": "class_A.count > 0",
        "raise_error": True,
    },
    {
        "case": "user does not write count",
        "query": "JOB.class_A > 0",
        "raise_error": True,
    },
    {
        "case": "user can provide expressions separated by OR and AND",
        "query": "JOB.class_A.count > 0 AND JOB2.class_B.count == 3 OR JOB2.class_C.count < 3",
        "raise_error": False,
    },
    {
        "case": "user can provide expressions with parenthesis",
        "query": "JOB.class_A.count > 0 AND (JOB2.class_B.count == 3 OR JOB2.class_C.count < 3)",
        "raise_error": False,
    },
    {
        "case": "user can add spaces where it does not break the query",
        "query": "JOB. class_A.  count > 0 AND      JOB2.class_B. count ==   3",
        "raise_error": False,
    },
    {
        "case": "user did not close a parenthesis",
        "query": "JOB.class_A.count > 0 AND (JOB2.class_B.count == 3 OR JOB2.class_C.count < 3",
        "raise_error": True,
    },
    {
        "case": "user can have complex job and ategory name",
        "query": "JoB46_Hhzef*bzf66.class_Auzf657bdh----_.count > 0 ",
        "raise_error": False,
    },
]


def test_category_search_queries():
    for test in TEST_CASES:
        case, query, raise_error = (
            test.get("case"),
            test.get("query"),
            test.get("raise_error"),
        )
        if raise_error:
            with pytest.raises(ValueError):
                validate_category_search_query(query)
        else:
            validate_category_search_query(query)
