"""CLI's project member remove subcommand"""

import warnings
from typing import Dict, Iterable, List, Optional, cast

import click

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.helpers import get_kili_client
from kili.cli.project.member.helpers import (
    check_exclusive_options,
    collect_members_from_csv,
    collect_members_from_emails,
    collect_members_from_project,
)
from kili.graphql import QueryOptions
from kili.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)


@click.command(name="rm")
@Options.api_key
@Options.endpoint
@Arguments.emails
@Options.project_id
@from_csv(["email"], ["role"])
@click.option(
    "--all",
    "all_members",
    type=bool,
    is_flag=True,
    default=False,
    help="Remove all users from project",
)
# pylint: disable=too-many-arguments
def remove_member(
    api_key: Optional[str],
    endpoint: Optional[str],
    emails: Optional[Iterable[str]],
    project_id: str,
    csv_path: Optional[str],
    all_members: bool,
):
    """Remove members from a Kili project

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member rm \\
            --project-id <project_id> \\
            john.doe@test.com
        ```
        ```
        kili project member rm \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv

        ```
        ```
        kili project member rm \\
            --project-id <project_id> \\
            --all
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    check_exclusive_options(csv_path, None, emails, all_members)

    if csv_path is not None:
        members_to_rm = collect_members_from_csv(csv_path, None)
    elif all_members:
        members_to_rm = collect_members_from_project(kili, project_id, None)
    else:
        assert emails, (
            "When a --csv-path and --all-members are not called, you must add several email"
            " addresses as arguments."
        )
        members_to_rm = collect_members_from_emails(emails, None)

    count = 0
    existing_members = cast(
        List[Dict],
        ProjectUserQuery(kili.auth.client)(
            where=ProjectUserWhere(project_id=project_id),
            fields=[
                "activated",
                "user.email",
                "id",
            ],
            options=QueryOptions(disable_tqdm=True),
        ),
    )
    existing_members_email_map = {
        member["user"]["email"]: member["id"] for member in existing_members if member["activated"]
    }

    for member in members_to_rm:
        email = member["email"]
        if email in existing_members_email_map.keys():
            kili.delete_from_roles(role_id=existing_members_email_map[email])
            count += 1
        else:
            warnings.warn(f"{email} is not an active member of the project.")

    print(f"{count} member(s) have been successfully removed from project: {project_id}")
