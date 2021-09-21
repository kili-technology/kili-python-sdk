"""
Queries of dataset mutations
"""

from .fragments import DATASET_FRAGMENT

GQL_APPEND_TO_DATASET = f'''
mutation(
    $data: AppendToDatasetData!
    $where: DatasetWhere!
) {{
  data: appendToDataset(
    data: $data,
    where: $where
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_APPEND_TO_DATASET_USERS = f'''
mutation(
    $data: AppendToDatasetUsersData!
    $where: DatasetWhere!
) {{
  data: appendToDatasetUsers(
    data: $data,
    where: $where
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_APPEND_DATASETS_TO_PROJECT = '''
mutation(
    $data: AppendDatasetsToProjectData!
    $where: ProjectWhere!
) {
  data: appendDatasetsToProject(
    data: $data,
    where: $where
  )
}
'''

GQL_CREATE_DATASET = f'''
mutation(
    $data: CreateDatasetData!
) {{
  data: createDataset(
    data: $data,
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_DELETE_DATASET = f'''
mutation(
    $where: DatasetWhere!
) {{
  data: deleteDataset(
    where: $where
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_UPDATE_PROPERTIES_IN_DATASET = f'''
mutation(
    $datasetId: ID!
    $assetType: InputType!
    $name: String!
) {{
  data: updatePropertiesInDataset(
    data: {{
      assetType: $assetType,
      name: $name
    }}
    where: {{
      id: $datasetId
    }}) {{
    {DATASET_FRAGMENT}
  }}
}}
'''
