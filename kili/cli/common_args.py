"""Common arguments and options for the CLI"""
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Options:  # pylint: disable=too-few-public-methods
    """Common options for the CLI"""

    api_key = click.option(
        '--api-key', type=str, default=None,
        help=(
            'Your Kili API key. '
        ),
        show_default=(
            '"KILI_API_KEY" environment variable'
        )
    )

    endpoint = click.option(
        '--endpoint', type=str, default=None,
        help=(
            'Kili API Endpoint. '
        ),
        show_default=(
            '"KILI_API_ENDPOINT" environment variable,'
            ' Kili SAAS: "https://cloud.kili-technology.com/api/label/v2/graphql"'
        )
    )

    tablefmt = click.option('--stdout-format', 'tablefmt', type=str, default='plain',
                            help='Defines how the output table is formatted '
                            '(see https://pypi.org/project/tabulate/, default: plain).')
