"""Tests for category search validation."""

import pytest

from kili.core.helpers import validate_category_search_query


@pytest.mark.parametrize(
    "case, query, raise_error",
    [
        (
            "user does not provide job",
            "class_A.count > 0",
            True,
        ),
        (
            "user does not write count",
            "JOB.class_A > 0",
            True,
        ),
        (
            "user can provide expressions separated by OR and AND",
            "JOB.class_A.count > 0 AND JOB2.class_B.count == 3 OR JOB2.class_C.count < 3",
            False,
        ),
        (
            "user can provide expressions with parenthesis",
            "JOB.class_A.count > 0 AND (JOB2.class_B.count == 3 OR JOB2.class_C.count < 3)",
            False,
        ),
        (
            "user can add spaces where it does not break the query",
            "JOB. class_A.  count > 0 AND      JOB2.class_B. count ==   3",
            False,
        ),
        (
            "user did not close a parenthesis",
            "JOB.class_A.count > 0 AND (JOB2.class_B.count == 3 OR JOB2.class_C.count < 3",
            True,
        ),
        (
            "user can have complex job and ategory name",
            "JoB46_Hhzef*bzf66.class_Auzf657bdh----_.count > 0 ",
            False,
        ),
    ],
)
def test_category_search_queries(case: str, query: str, raise_error: bool):
    if raise_error:
        with pytest.raises(ValueError):
            validate_category_search_query(query)
    else:
        validate_category_search_query(query)
