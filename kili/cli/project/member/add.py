"""CLI's project member add subcommand"""

from typing import Optional
import warnings
import click
from kili.cli.project.member.helpers import (
    ROLES,
    collect_members_from_csv,
    collect_members_from_emails,
    collect_members_from_project)

from kili.client import Kili
from kili.cli.common_args import Options


# pylint: disable=too-many-arguments
@click.command()
@Options.api_key
@Options.endpoint
@click.argument('emails', type=str, required=False, nargs=-1)
@click.option('--project-id', type=str, required=True,
              help='Id of the project to add members to')
@click.option('--role', type=click.Choice(ROLES), default=None,
              show_default='LABELER',
              help='Project role of the added user(s).')
@ click.option('--from-csv', 'csv_path', type=click.Path(),
               help=("path to a csv file with 'email' header,"
               " optionnal header 'role' can be use.")
               )
@click.option('--from-project', 'project_id_src', type=str,
              help='project_id of another Kili project to copy the users from')
def add_member(api_key: Optional[str],
               endpoint: Optional[str],
               emails: Optional[str],
               project_id: str,
               role: Optional[str],
               csv_path:  Optional[str],
               project_id_src: Optional[str],
               ):
    """Add members to a Kili project

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member add \\
            --project-id <project_id> \\
            --role REVIEWER \\
            john.doe@test.com jane.doe@test.com
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-project <project_id_scr>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    if ((csv_path is not None) + (project_id_src is not None) + (len(emails) > 0)) > 1:
        raise ValueError(
            'Options --from-csv, --from-project and emails are exclusive.')

    if csv_path is not None:
        members_to_add = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_add = collect_members_from_project(
            kili, project_id_src, role)
    else:
        members_to_add = collect_members_from_emails(emails, role)

    count = 0
    existing_members = kili.project_users(
        project_id=project_id, disable_tqdm=True)
    existing_members = [member['user']['email']
                        for member in existing_members if member['activated']]

    for member in members_to_add:
        if member['email'] in existing_members:
            already_member = member['email']
            warnings.warn(f'{already_member} is already an active member of the project.'
                          ' Use kili project member update to update role.')
        else:
            kili.append_to_roles(project_id=project_id,
                                 user_email=member['email'], role=member['role'])
            count += 1

    print(f'{count} users have been successfully added to project: {project_id}')
