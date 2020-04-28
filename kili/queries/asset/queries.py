from .fragments import ASSET_FRAGMENT

GQL_GET_ASSET = f'''
query($assetID: ID!) {{
  data: getAsset(assetID: $assetID) {{
    {ASSET_FRAGMENT}
  }}
}}
'''


def GQL_ASSETS(fragment):
    return f'''
query(
    $assetID: ID
    $projectID: ID
    $skip: Int!
    $first: PageSize!
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
  data: assets(
    where: {{
      id: $assetID
      project: {{
        id: $projectID
      }}
      externalIdIn: $externalIdIn
      statusIn: $statusIn
      authorIn: $authorIn
      consensusMarkGte: $consensusMarkGte
      consensusMarkLte: $consensusMarkLte
      honeypotMarkGte: $honeypotMarkGte
      honeypotMarkLte: $honeypotMarkLte
      skipped: $skipped
      label: {{
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
    }}
    skip: $skip
    first: $first
  ) {{
    {fragment}
  }}
}}
'''


GQL_GET_NEXT_ASSET_FROM_LABEL = f'''
query($labelAssetIDs: [ID!]) {{
  data: getNextAssetFromLabel(labelAssetIDs: $labelAssetIDs, where: {{}}) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_GET_NEXT_ASSET_FROM_PROJECT = f'''
query($projectID: ID!) {{
  data: getNextAssetFromProject(projectID: $projectID) {{
    {ASSET_FRAGMENT}
  }}
}}
'''

GQL_ASSETS_COUNT = f'''
query(
    $assetID: ID
    $projectID: ID
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
  data: countAssets(
    where: {{
      id: $assetID
      project: {{
        id: $projectID
      }}
      externalIdIn: $externalIdIn
      statusIn: $statusIn
      authorIn: $authorIn
      consensusMarkGte: $consensusMarkGte
      consensusMarkLte: $consensusMarkLte
      honeypotMarkGte: $honeypotMarkGte
      honeypotMarkLte: $honeypotMarkLte
      skipped: $skipped
      label: {{
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
    }})
}}
'''
