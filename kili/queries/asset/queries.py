from .fragments import ASSET_FRAGMENT, ASSET_FRAGMENT_SIMPLIFIED

GQL_GET_ASSET = f'''
query($assetID: ID!) {{
  data: getAsset(assetID: $assetID) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_GET_ASSETS_WITH_SEARCH = f'''
query(
    $projectID: ID!
    $skip: Int!
    $first: Int!
    $externalIdIn: [String]
    $statusIn: [String]
    $authorIn: [String]
    $consensusMarkGte: Float
    $consensusMarkLte: Float
    $honeypotMarkGte: Float
    $honeypotMarkLte: Float
    $skipped: Boolean
    $labelExternalIdContains: String
    $labelTypeIn: [String]
    $labelStatusIn: [String]
    $labelAuthorIn: [String]
    $labelConsensusMarkGte: Float
    $labelConsensusMarkLte: Float
    $labelHoneypotMarkGte: Float
    $labelHoneypotMarkLte: Float
    $labelCreatedAtGte: String
    $labelCreatedAtLte: String
    $labelSkipped: Boolean

) {{
  data: getAssetsWithSearch(
    projectID: $projectID
    skip: $skip
    first: $first
    assetsWhere: {{
      externalIdIn: $externalIdIn
      statusIn: $statusIn
      authorIn: $authorIn
      consensusMarkGte: $consensusMarkGte
      consensusMarkLte: $consensusMarkLte
      honeypotMarkGte: $honeypotMarkGte
      honeypotMarkLte: $honeypotMarkLte
      skipped: $skipped
    }}
    labelsWhere: {{
      externalIdContains: $labelExternalIdContains
      typeIn: $labelTypeIn
      statusIn: $labelStatusIn
      authorIn: $labelAuthorIn
      consensusMarkGte: $labelConsensusMarkGte
      consensusMarkLte: $labelConsensusMarkLte
      honeypotMarkGte: $labelHoneypotMarkGte
      honeypotMarkLte: $labelHoneypotMarkLte
      createdAtGte: $labelCreatedAtGte
      createdAtLte: $labelCreatedAtLte
      skipped: $labelSkipped
    }}
  ) {{
    {ASSET_FRAGMENT_SIMPLIFIED}
  }}
}}
'''

GQL_GET_ASSETS_BY_EXTERNAL_ID = f'''
query($projectID: ID!, $externalID: String!) {{
  data: getAssetsByExternalId(projectID: $projectID, externalID: $externalID) {{
    {ASSET_FRAGMENT_SIMPLIFIED}
  }}
}}
'''

GQL_GET_NEXT_ASSET_FROM_LABEL = f'''
query($labelAssetIDs: [ID!]) {{
  data: getNextAssetFromLabel(labelAssetIDs: $labelAssetIDs, where: {{}}) {{
    {ASSET_FRAGMENT_SIMPLIFIED}
  }}
}}
'''

GQL_GET_NEXT_ASSET_FROM_PROJECT = f'''
query($projectID: ID!) {{
  data: getNextAssetFromProject(projectID: $projectID) {{
    {ASSET_FRAGMENT_SIMPLIFIED}
  }}
}}
'''

GQL_EXPORT_ASSETS = f'''
query($projectID: ID!) {{
  exportAssets(projectID: $projectID) {{
    {ASSET_FRAGMENT_SIMPLIFIED}
  }}
}}
'''

GQL_COUNT_ASSETS_WITH_SEARCH = f'''
query(
    $projectID: ID!
    $externalIdIn: [String]
    $statusIn: [String]
    $authorIn: [String]
    $consensusMarkGte: Float
    $consensusMarkLte: Float
    $honeypotMarkGte: Float
    $honeypotMarkLte: Float
    $skipped: Boolean
    $labelExternalIdContains: String
    $labelTypeIn: [String]
    $labelStatusIn: [String]
    $labelAuthorIn: [String]
    $labelConsensusMarkGte: Float
    $labelConsensusMarkLte: Float
    $labelHoneypotMarkGte: Float
    $labelHoneypotMarkLte: Float
    $labelCreatedAtGte: String
    $labelCreatedAtLte: String
    $labelSkipped: Boolean

) {{
  data: countAssetsWithSearch(
    projectID: $projectID
    assetsWhere: {{
      externalIdIn: $externalIdIn
      statusIn: $statusIn
      authorIn: $authorIn
      consensusMarkGte: $consensusMarkGte
      consensusMarkLte: $consensusMarkLte
      honeypotMarkGte: $honeypotMarkGte
      honeypotMarkLte: $honeypotMarkLte
      skipped: $skipped
    }}
    labelsWhere: {{
      externalIdContains: $labelExternalIdContains
      typeIn: $labelTypeIn
      statusIn: $labelStatusIn
      authorIn: $labelAuthorIn
      consensusMarkGte: $labelConsensusMarkGte
      consensusMarkLte: $labelConsensusMarkLte
      honeypotMarkGte: $labelHoneypotMarkGte
      honeypotMarkLte: $labelHoneypotMarkLte
      createdAtGte: $labelCreatedAtGte
      createdAtLte: $labelCreatedAtLte
      skipped: $labelSkipped
    }})
}}
'''
