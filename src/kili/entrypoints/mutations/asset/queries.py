"""Queries of asset mutations."""

GQL_ASSIGN_ASSETS = """
mutation assignAssets(
    $where: AssetWhere!,
    $userIds: [String!]!
) {
    data: assignAssets(
        where: $where,
        userIds: $userIds
    ) {
      succeeded {
        assetId
        externalId
      }
      declined {
        assetId
        externalId
      }
      failed {
        assetId
        externalId
        details
      }
    }
  }
"""

GQL_UPDATE_PROPERTIES_IN_ASSETS = """
mutation(
    $whereArray: [AssetWhere!]!
    $dataArray: [AssetData!]!
) {
  data: updatePropertiesInAssets(
    where: $whereArray,
    data: $dataArray
  ) {
    id
  }
}
"""

GQL_DELETE_ASSETS = """
mutation($where: AssetWhere!) {
  data: deleteAssets(where: $where) {
    succeeded {
      assetId
      externalId
    }
    declined {
      assetId
      externalId
    }
    failed {
      assetId
      externalId
      details
    }
  }
}
"""

GQL_ADD_ASSETS_TO_REVIEW = """
mutation($where: AssetWhere!) {
  data: addAssetsToReview(where: $where) {
    succeeded {
      assetId
      externalId
    }
    declined {
      assetId
      externalId
    }
    failed {
      assetId
      externalId
      details
    }
  }
}
"""

GQL_SEND_ASSETS_BACK_TO_QUEUE = """
mutation($where: AssetWhere!) {
  data: sendAssetsBackToQueue(where: $where) {
    succeeded {
      assetId
      externalId
    }
    declined {
      assetId
      externalId
    }
    failed {
      assetId
      externalId
      details
    }
  }
}
"""

GQL_SKIP_ASSET = """
mutation SkipAsset($reason: String!, $where: AssetWhere!) {
  skipAsset(reason: $reason, where: $where) {
    id
  }
}
"""

GQL_UNSKIP_ASSET = """
mutation UnskipAsset($projectId: ID!, $assetId: ID!) {
  unskipAsset(projectId: $projectId, assetId: $assetId)
}
"""
