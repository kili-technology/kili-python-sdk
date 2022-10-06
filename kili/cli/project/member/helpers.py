"""CLI's Project Member common functions"""

import re
import warnings
from typing import Dict, Iterable, List, Optional, cast

from kili.cli.common_args import ROLES
from kili.cli.helpers import collect_from_csv

REGEX_EMAIL = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")


def type_check_member(key, value):
    """type check value based on key"""
    if key == "email" and not re.search(REGEX_EMAIL, value):
        return f"{value} is not a valid email address, "

    if key == "role" and value not in ROLES:
        return f"{value} is not a valid role, "

    return ""


def collect_members_from_csv(csv_path: str, role: Optional[str]):
    """read a csv with to collect members and role"""
    members_to_add = collect_from_csv(
        csv_path=csv_path,
        required_columns=["email"],
        optional_columns=["role"],
        type_check_function=type_check_member,
    )

    if len(members_to_add) == 0:
        raise ValueError(f"No active member were found in csv: {csv_path}")

    if "role" in members_to_add[0].keys():
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


def collect_members_from_project(kili, project_id_source: str, role: Optional[str]):
    """copy members from project of id project_id_source"""
    members = []

    if role is not None:
        raise ValueError("--role cannot be used if the argument passed is a Kili project_id")

    try:
        users = cast(
            List[Dict],
            kili.project_users(
                project_id=project_id_source,
                fields=["role", "user.email", "activated"],
                disable_tqdm=True,
            ),
        )
        for user in users:
            if user["activated"]:
                members.append({"email": user["user"]["email"], "role": user["role"]})
    except:
        # pylint: disable=raise-missing-from
        raise ValueError(f"{project_id_source} is not recognized as a Kili project_id")

    if len(members) == 0:
        raise ValueError(f"No active member were found in project with id {project_id_source}")

    return members


def collect_members_from_emails(emails: Iterable[str], role: Optional[str]):
    """collect members with email address from emails"""
    if role is None:
        role = "LABELER"
    members_to_add = []
    for email in emails:
        if re.search(REGEX_EMAIL, email):
            members_to_add.append({"email": email, "role": role})
        else:
            warnings.warn(f"{email} is not a valid email address,")

    if len(members_to_add) == 0:
        raise ValueError("No valid email adresses were provided")

    return members_to_add


def check_exclusive_options(
    csv_path: Optional[str],
    project_id_src: Optional[str],
    emails: Optional[Iterable[str]],
    all_members: Optional[bool],
) -> None:
    """Forbid mutual use of options and argument(s)"""
    if not emails:
        return None
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
    return None
