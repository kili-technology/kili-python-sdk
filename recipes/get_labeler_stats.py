import pandas as pd

from kili.authentication import KiliAuth
from kili.playground import Playground
from settings import *

kauth = KiliAuth(email=EMAIL,
                 password=PASSWORD,
                 api_endpoint=API_ENDPOINT)
playground = Playground(kauth)

df = pd.DataFrame(columns=['Project', 'Date', 'Email'])
for project_id in SOURCE_PROJECT_ID.split(','):
    project = playground.get_project(project_id=project_id)
    assets = playground.get_assets(project_id=project_id)
    title = project['title']
    for asset in assets:
        for label in asset['labels']:
            created_at = label['createdAt'][:10]
            author_email = label['author']['email']
            df = df.append({'Project': title, 'Date': created_at,
                            'Email': author_email}, ignore_index=True)
df_grouped = df.groupby(['Project', 'Date', 'Email']).size()
df_grouped.to_excel(f"labeler-stats.xlsx")
