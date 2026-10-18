"""Tests for the conversion of step filters given by name into filters by id."""

import pytest

from kili.presentation.client.helpers.filter_conversion import (
    extract_step_id_and_status_filters_from_project_steps,
    resolve_step_filters,
)

# Step names are unique per group only: both groups have a "Review".
PROJECT_STEPS = [
    {"id": "label-1", "name": "Label"},
    {"id": "review-1", "name": "Review"},
    {"id": "label-2", "name": "Label 2"},
    {"id": "review-2", "name": "Review"},
]

NO_STEP_FILTER = {
    "step_id_in": None,
    "step_id_not_in": None,
    "step_id_and_status_in": None,
    "step_id_and_status_not_in": None,
    "step_name_in": None,
    "step_name_not_in": None,
    "step_name_and_status_in": None,
    "step_name_and_status_not_in": None,
}


def test_a_step_name_and_status_filter_covers_the_step_of_every_group_using_the_name():
    filters = extract_step_id_and_status_filters_from_project_steps(
        PROJECT_STEPS, [("Review", "TO_DO"), ("Label", "DONE")]
    )

    assert filters == [("review-1", "TO_DO"), ("review-2", "TO_DO"), ("label-1", "DONE")]


def test_step_filters_given_by_id_are_kept_as_they_are():
    filters = resolve_step_filters(
        PROJECT_STEPS,
        **{**NO_STEP_FILTER, "step_id_in": ["review-2"], "step_id_not_in": ["label-1"]},
    )

    assert filters == (["review-2"], ["label-1"], None, None)


def test_step_filters_given_by_name_are_converted_to_ids():
    filters = resolve_step_filters(
        PROJECT_STEPS,
        **{
            **NO_STEP_FILTER,
            "step_name_in": ["Review"],
            "step_name_and_status_not_in": [("Label 2", "SKIPPED")],
        },
    )

    assert filters == (["review-1", "review-2"], None, None, [("label-2", "SKIPPED")])


@pytest.mark.parametrize(
    ("by_id", "by_name", "value_by_id", "value_by_name"),
    [
        ("step_id_in", "step_name_in", ["review-1"], ["Review"]),
        ("step_id_not_in", "step_name_not_in", ["review-1"], ["Review"]),
        (
            "step_id_and_status_in",
            "step_name_and_status_in",
            [("review-1", "DONE")],
            [("Review", "DONE")],
        ),
        (
            "step_id_and_status_not_in",
            "step_name_and_status_not_in",
            [("review-1", "DONE")],
            [("Review", "DONE")],
        ),
    ],
)
def test_a_step_filter_is_given_either_by_id_or_by_name(by_id, by_name, value_by_id, value_by_name):
    with pytest.raises(ValueError, match="both given"):
        resolve_step_filters(
            PROJECT_STEPS, **{**NO_STEP_FILTER, by_id: value_by_id, by_name: value_by_name}
        )
