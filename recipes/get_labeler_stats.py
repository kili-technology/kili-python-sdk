from datetime import datetime

import click
import pandas as pd

from kili.client import Kili
from kili.graphql import QueryOptions
from kili.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.services.project import get_project_field


@click.command()
@click.option(
    "--api-endpoint",
    default=None,
    help="Endpoint of GraphQL client",
    show_default=(
        "'KILI_API_ENDPOINT' environment variable or "
        "'https://cloud.kili-technology.com/api/label/v2/graphql' if not set"
    ),
)
def main(api_endpoint):
    api_key = input("Enter API KEY: ")
    source_project_id = input(
        'Enter project IDs (separate them by "," if you want to provide several): '
    )

    kili = Kili(api_key=api_key, api_endpoint=api_endpoint)

    df = pd.DataFrame(columns=["Project", "Date", "Email"])
    for project_id in source_project_id.split(","):
        project_title = get_project_field(kili, project_id, "title")
        assets = AssetQuery(kili.auth.client)(
            AssetWhere(project_id=project_id),
            ["labels.createdAt", "createdAt.author.email"],
            QueryOptions(disable_tqdm=False),
        )
        for asset in assets:
            for label in asset["labels"]:
                created_at = label["createdAt"][:10]
                author_email = label["author"]["email"]
                df = df.append(
                    {"Project": project_title, "Date": created_at, "Email": author_email},
                    ignore_index=True,
                )
    df_grouped = df.groupby(["Project", "Date", "Email"]).size()
    time = datetime.now().strftime("%Y%m%d%H%M")
    df_grouped.to_excel(f"labeler-stats-{time}.xlsx")


if __name__ == "__main__":
    main()