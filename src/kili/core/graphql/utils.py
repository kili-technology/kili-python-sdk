from typing import Sequence

from typeguard import typechecked


@typechecked
def fragment_builder(fields: Sequence[str]) -> str:
    """Build a GraphQL fragment from a sequence of fields to query.

    Args:
        fields: The sequence of fields to query
    """
    fragment = ""

    # split a field and its subfields (e.g. "roles.user.id" -> ["roles", "user.id"])
    subfields = [field.split(".", 1) for field in fields if "." in field]

    if subfields:
        # get the root fields (e.g. "roles" in "roles.user.id")
        root_fields = {subfield[0] for subfield in subfields}
        for root_field in root_fields:
            # get the subfields of the root field (e.g. "user.id" in "roles.user.id")
            fields_subquery = [subfield[1] for subfield in subfields if subfield[0] == root_field]
            # build the subquery fragment (e.g. "user{id}" in "roles{user{id}}")
            new_fragment = fragment_builder(fields_subquery)
            # add the subquery to the fragment
            fragment += f" {root_field}{{{new_fragment}}}"

        # remove the fields that have been queried in subqueries (e.g. "roles.user.id")
        fields = [field for field in fields if "." not in field]

    for field in fields:
        fragment += f" {field}"

    return fragment
