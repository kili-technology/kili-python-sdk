"""Common arguments and options for the CLI"""
from typing import List

import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
ROLES = ["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"]


class Options:  # pylint: disable=too-few-public-methods
    """Common options for the CLI"""

    api_key = click.option(
        "--api-key",
        type=str,
        default=None,
        help=("Your Kili API key. "),
        show_default=('"KILI_API_KEY" environment variable'),
    )

    endpoint = click.option(
        "--endpoint",
        type=str,
        default=None,
        help=("Kili API Endpoint. "),
        show_default=(
            '"KILI_API_ENDPOINT" environment variable,'
            ' Kili SAAS: "https://cloud.kili-technology.com/api/label/v2/graphql"'
        ),
    )

    project_id = click.option("--project-id", type=str, required=True, help="Id of the project")

    tablefmt = click.option(
        "--stdout-format",
        "tablefmt",
        type=str,
        default="plain",
        help="Defines how the output table is formatted "
        "(see https://pypi.org/project/tabulate/, default: plain).",
    )

    from_project = click.option(
        "--from-project",
        "project_id_src",
        type=str,
        help="project_id of another Kili project",
    )

    role = click.option(
        "--role",
        type=click.Choice(ROLES),
        default=None,
        show_default="LABELER",
        help="Project role of the added user(s).",
    )

    script_name = click.option(
        "--script-name",
        type=str,
        default=None,
        help=(
            "Script's name in Kili database."
            "If not provided, it will be the file name on your machine"
        ),
    )

    verbose = click.option(
        "--verbose", type=bool, is_flag=True, default=False, help="Show more logs"
    )


def from_csv(required_columns: List[str], optionnal_columns: List[str]):
    """--from-csv shared click option"""
    help_ = (
        "path to a csv file with required columns:"
        + ", ".join(required_columns)
        + " required columns: "
        + ", ".join(optionnal_columns)
    )

    return click.option(
        "--from-csv",
        "csv_path",
        type=click.Path(),
        help=help_,
    )


class Arguments:  # pylint: disable=too-few-public-methods
    """Common arguments for the CLI"""

    files = click.argument("files", type=click.Path(), required=False, nargs=-1)

    file_path = click.argument("file_path", type=str, required=False, nargs=1)

    emails = click.argument("emails", type=str, required=False, nargs=-1)

    project_id = click.argument("project_id", type=str, required=True)
