"""CLI's Project Member common functions."""

import re
import warnings
from typing import TYPE_CHECKING, Callable, Iterable, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.client import Kili
from kili.core.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)
from kili.entrypoints.cli.common_args import ROLES
from kili.entrypoints.cli.helpers import collect_from_csv

if TYPE_CHECKING:
    from kili.adapters.http_client import HttpClient

REGEX_EMAIL = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")


def type_check_member(key, value):
    """Type check value based on key."""
    if key == "email" and not re.search(REGEX_EMAIL, value):
        return f"{value} is not a valid email address, "

    if key == "role" and value not in ROLES:
        return f"{value} is not a valid role, "

    return ""


def collect_members_from_csv(csv_path: str, role: Optional[str]):
    """Read a csv with to collect members and role."""
    type_check_function: Callable[[str, str, Optional[HttpClient]], str] = (
        lambda key, value, z: type_check_member(key, value)
    )
    members_to_add = collect_from_csv(
        csv_path=csv_path,
        required_columns=["email"],
        optional_columns=["role"],
        type_check_function=type_check_function,
    )

    if len(members_to_add) == 0:
        raise ValueError(f"No active member were found in csv: {csv_path}")

    if "role" in members_to_add[0]:
        if role is not None:
            raise ValueError(
                "--role cannot be used if the argument passed is a path to a csv file with roles"
            )
    else:
        if role is None:
            role = "LABELER"
        for member in members_to_add:
            member["role"] = role

    return members_to_add


def collect_members_from_project(kili: Kili, project_id_source: str, role: Optional[str]):
    """Copy members from project of id project_id_source."""
    activated_members = []

    if role is not None:
        raise ValueError("--role cannot be used if the argument passed is a Kili project_id")

    existing_members = ProjectUserQuery(kili.graphql_client, kili.http_client)(
        where=ProjectUserWhere(project_id=project_id_source),
        fields=["role", "user.email", "activated"],
        options=QueryOptions(disable_tqdm=True),
    )
    for existing_member in existing_members:
        if existing_member["activated"]:
            activated_members.append(
                {"email": existing_member["user"]["email"], "role": existing_member["role"]}
            )

    if len(activated_members) == 0:
        raise ValueError(
            f"No active member were found in project with id {project_id_source} or the project"
            " does not exist"
        )

    return activated_members


def collect_members_from_emails(emails: Iterable[str], role: Optional[str]):
    """Collect members with email address from emails."""
    if role is None:
        role = "LABELER"
    members_to_add = []
    for email in emails:
        if re.search(REGEX_EMAIL, email):
            members_to_add.append({"email": email, "role": role})
        else:
            warnings.warn(f"{email} is not a valid email address,", stacklevel=2)

    if len(members_to_add) == 0:
        raise ValueError("No valid email adresses were provided")

    return members_to_add


def check_exclusive_options(
    csv_path: Optional[str],
    project_id_src: Optional[str],
    emails: Optional[Iterable[str]],
    all_members: Optional[bool],
) -> None:
    """Forbid mutual use of options and argument(s)."""
    if not emails:
        return
    emails = list(emails)
    if all_members is None:
        if (csv_path is not None) + (project_id_src is not None) + (len(emails) > 0) > 1:
            raise ValueError(
                "emails arguments and options --from-csv and --from-project are exclusive."
            )
        if (csv_path is not None) + (project_id_src is not None) + (len(emails) > 0) == 0:
            raise ValueError(
                "You must either provide emails arguments or use one option from "
                "--from-csv or --from-project"
            )

    else:
        if (csv_path is not None) + (all_members is True) + (len(emails) > 0) > 1:
            raise ValueError("emails arguments and options --from-csv and --all are exclusive.")
        if (csv_path is not None) + (all_members is not None) + (len(emails) > 0) == 0:
            raise ValueError(
                "You must either provide emails arguments or use one option --from-csv or --all"
            )
    return
