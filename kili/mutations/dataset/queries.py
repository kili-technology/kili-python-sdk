from .fragments import DATASET_FRAGMENT

GQL_APPEND_TO_DATASET = f'''
mutation(
    $contentArray: [String!]
    $datasetId: String!
    $externalIdArray: [String!]
) {{
  data: appendToDataset(
    contentArray: $contentArray,
    datasetId: $datasetId,
    externalIdArray: $externalIdArray
  ) {{
    {DATASET_FRAGMENT}
  }}
}}
'''

GQL_APPEND_DATASETS_TO_PROJECT = f'''
mutation(
    $projectId: String!
    $datasetIds: [String!]
    $datasetAssetIds: [String!]
) {{
  data: appendDatasetsToProject(
    projectId: $projectId,
    datasetIds: $datasetIds,
    datasetAssetIds: $datasetAssetIds
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
    $datasetId: ID!
) {{
  data: deleteDataset(
    where: {{
      id: $datasetId
    }}) {{
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