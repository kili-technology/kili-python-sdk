import click
from datetime import datetime
import pandas as pd
import getpass

from kili.client import Kili


@click.command()
@click.option('--api_endpoint', default='https://cloud.kili-technology.com/api/label/v2/graphql',
              help='Endpoint of GraphQL client')
def main(api_endpoint):
    api_key = input('Enter API KEY: ')
    source_project_id = input(
        'Enter project IDs (separate them by "," if you want to provide several): ')

    kili = Kili(api_key=api_key,
                     api_endpoint=api_endpoint)

    df = pd.DataFrame(columns=['Project', 'Date', 'Email'])
    for project_id in source_project_id.split(','):
        project = kili.projects(project_id=project_id)[0]
        assets = kili.assets(project_id=project_id)
        title = project['title']
        for asset in assets:
            for label in asset['labels']:
                created_at = label['createdAt'][:10]
                author_email = label['author']['email']
                df = df.append({'Project': title, 'Date': created_at,
                                'Email': author_email}, ignore_index=True)
    df_grouped = df.groupby(['Project', 'Date', 'Email']).size()
    time = datetime.now().strftime('%Y%m%d%H%M')
    df_grouped.to_excel(f'labeler-stats-{time}.xlsx')


if __name__ == '__main__':
    main()
