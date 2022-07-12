"""CLI's project member update subcommand"""

from typing import Optional
import warnings
import click
from kili.cli.project.member.helpers import (ROLES,
                                             collect_members_from_csv,
                                             collect_members_from_emails,
                                             collect_members_from_project)

from kili.client import Kili
from kili.cli.common_args import Options


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
               help=('path to a csv file with email in the first column.'
               ' A second column can be used to use one-to-one role.')
               )
@click.option('--from-project', 'project_id_src', type=str,
              help='project_id of another Kili project to copy the users from')
# pylint: disable=too-many-arguments
def update_member(api_key: Optional[str],
                  endpoint: Optional[str],
                  emails: Optional[str],
                  project_id: str,
                  role: Optional[str],
                  csv_path:  Optional[str],
                  project_id_src: Optional[str],
                  ):
    """Update member's role of a Kili project

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member update\\
            --project-id <project_id> \\
            --role REVIEWER \\
            john.doe@test.com
        ```
        ```
        kili project member update \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv
        ```
        ```
        kili project member update \\
            --project-id <project_id> \\
            --from-project <project_id_scr>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)

    if ((csv_path is not None) + (project_id_src is not None) + (len(emails) > 0)) > 1:
        raise ValueError(
            'Options --from-csv, --from-project and emails are exclusive.')

    if csv_path is not None:
        members_to_update = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_update = collect_members_from_project(
            kili, project_id_src, role)
    else:
        members_to_update = collect_members_from_emails(emails, role)

    count = 0

    existing_members = kili.project_users(
        project_id=project_id, disable_tqdm=True)
    existing_members = {member['user']['email']: {
        'role_id': member['id'],
        'user_id': member['user']['id'],
        'role': member['role']
    }
        for member in existing_members if member['activated']}

    for member in members_to_update:
        email = member['email']
        if email in existing_members.keys():
            if existing_members[email]['role'] != member['role']:
                kili.update_properties_in_role(
                    role_id=existing_members[email]['role_id'],
                    project_id=project_id,
                    user_id=existing_members[email]['user_id'],
                    role=member['role'])
                count += 1
            else:
                warnings.warn(f'{email} is already an active member of the project'
                              ' with the same role.')
        else:
            warnings.warn(f'{email} is not an active member of the project.'
                          ' Use kili project member add to add member.')

    print(f"{count} user's role have been successfully updated in project: {project_id}")
