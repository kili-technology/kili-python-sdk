from .fragments import DATASET_FRAGMENT

GQL_APPEND_TO_DATASET = f'''
mutation(
    $contentArray: [String!]
    $externalIdArray: [String!]
    $where: DatasetWhere!
) {{
  data: appendToDataset(
    contentArray: $contentArray,
    externalIdArray: $externalIdArray,
    where: $where
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_APPEND_DATASETS_TO_PROJECT = f'''
mutation(
    $datasetIds: [String!]
    $datasetAssetIds: [String!]
    $where: ProjectWhere!
) {{
  data: appendDatasetsToProject(
    datasetIds: $datasetIds,
    datasetAssetIds: $datasetAssetIds,
    where: $where
  )
}}
'''

GQL_CREATE_DATASET = f'''
mutation(
    $assetType: InputType!
    $name: String!
) {{
  data: createDataset(
    assetType: $assetType,
    name: $name
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
