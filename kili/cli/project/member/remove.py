"""CLI's project member remove subcommand"""

import csv
import os
import re
from typing import Dict, List, Optional, cast
import warnings
import click

from kili.client import Kili
from kili.cli.common_args import Options


REGEX_EMAIL = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def read_csv_user(csv_path: str, emails: List[str]):
    """read a csv with a user list and update emails and roles """
    with open(csv_path, 'r', encoding="utf-8") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if re.search(REGEX_EMAIL, row[0]):
                emails.append(row[0])


def extract_all_emails(kili, project_id: str, emails: List[str]):
    """extract all email adresses from user in project_id and update emails"""
    users = cast(
        List[Dict], kili.project_users(
            project_id=project_id,
            fields=[
                'user.email', 'activated'
            ],
            disable_tqdm=True))
    for user in users:
        if user['activated']:
            emails.append(user['user']['email'])
    if len(emails) == 0:
        warnings.warn(f'No active users found in project: {project_id}')


def remove_list_of_users(kili, project_id: str, emails: List[str]):
    """remove users listed in emails from project_id"""
    count = 0
    for email in emails:
        user = kili.project_users(
            project_id=project_id, email=email, disable_tqdm=True)
        if (len(user) > 0 and user[0]['activated']):
            kili.delete_from_roles(role_id=user[0]['id'])
            count += 1
        else:
            warnings.warn(f'{email} is not an active member of the project.')
    return count


@click.command()
@Options.api_key
@Options.endpoint
@click.argument('inputs', type=str, required=True, nargs=-1)
@ click.option('--project-id', type=str, required=True,
               help='Id of the project to add members to')
# pylint: disable=too-many-branches
def remove_member(api_key: Optional[str],
                  endpoint: Optional[str],
                  inputs: str,
                  project_id: str,
                  ):
    """Remove members to a Kili project

    Arguments can be: \n
        - string (with email format) \n
        - path to a csv file with email in the first column \n
        - all to remove all users \n

    You need to be an ADMIN of the organization or at
    least a TEAM_MANAGER in the project involved.

    \b
    !!! Examples
        ```
        kili project member rm \\
            john.doe@test.com \\
            --project-id <project_id>
        ```
        ```
        kili project member rm \\
            path/to/members.csv \\
            --project-id <project_id>
        ```
        ```
        kili project member rm \\
            all \\
            --project-id <project_id>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    emails = []
    for input_ in inputs:
        if os.path.exists(input_):
            read_csv_user(input_, emails)
        elif re.search(REGEX_EMAIL, input_):
            emails.append(input_)
        elif input_ == "all":
            extract_all_emails(kili, project_id, emails)
        else:
            raise ValueError(
                f'{input_} is not recognized as a csv file path '
                'nor an email adress nor "all"')

    count = remove_list_of_users(kili, project_id, emails)
    print(f'{count} users have been successfully removed from project: {project_id}')
