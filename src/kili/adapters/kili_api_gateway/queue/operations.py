"""GraphQL requests of the labeling and review interfaces' queue.

They are the requests label-frontend sends — the next asset (`loadAsset.ts`), the asset and its label
(`fetchAsset`, `getLabelOrPredictionForUser`), the lock (`useRenewLock.ts`), skip and send back — so a
script is served and held exactly as the interface serves and holds a person.
"""

GQL_GET_NEXT_ASSET_FROM_PROJECT = """
query getNextAssetFromProject($projectID: ID!) {
  data: getNextAssetFromProject(projectID: $projectID, doLock: true) {
    id
  }
}
"""

GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_PROJECT = """
query getNextAssetForReviewFromProject($projectID: ID!) {
  data: getNextAssetForReviewFromProject(projectID: $projectID, doLock: true) {
    id
  }
}
"""

GQL_GET_NEXT_ASSET_FROM_LABEL = """
query getNextAssetFromLabel(
  $labelAssetIDs: [ID!]
  $nonSubmittedViewedAssetIds: [ID!]!
  $projectId: ID!
) {
  data: getNextAssetFromLabel(
    labelAssetIDs: $labelAssetIDs
    nonSubmittedViewedAssetIds: $nonSubmittedViewedAssetIds
    projectId: $projectId
  ) {
    id
  }
}
"""

GQL_GET_NEXT_ASSET_FOR_REVIEW_FROM_LABEL = """
query getNextAssetForReviewFromLabel($labelAssetIDs: [ID!], $projectId: ID!) {
  data: getNextAssetForReviewFromLabel(labelAssetIDs: $labelAssetIDs, projectId: $projectId) {
    id
  }
}
"""

GQL_RENEW_LOCK = """
mutation renewLock($where: AssetWhere!) {
  data: renewLock(where: $where) {
    lockSucceeded
    reasons
  }
}
"""

GQL_DELETE_LOCKS = """
mutation deleteLocks($input: DeleteLocksInput!) {
  data: deleteLocks(input: $input)
}
"""

GQL_SUBMIT_LABEL = """
mutation frontendAppendToLabels($data: AppendToLabelsData!, $where: AssetWhere!) {
  data: frontendAppendToLabels(data: $data, where: $where) {
    id
  }
}
"""

GQL_SKIP_ASSET = """
mutation skipAsset($where: AssetWhere!, $reason: String) {
  data: skipAsset(where: $where, reason: $reason) {
    id
  }
}
"""

GQL_SEND_ASSET_BACK_TO_QUEUE = """
mutation sendAssetsBackToQueue($where: AssetWhere!) {
  data: sendAssetsBackToQueue(where: $where) {
    succeeded {
      assetId
    }
    declined {
      assetId
    }
    failed {
      assetId
      details
    }
  }
}
"""

GQL_GET_PROJECT_USER = """
query projectUsers($where: ProjectUserWhere!) {
  data: projectUsers(where: $where, first: 1, skip: 0) {
    role
    activated
  }
}
"""


def get_asset_query(fragment: str) -> str:
    """Return the query reading one asset by its id, as the interface reads the asset it serves.

    A labeler's `assets` query lists only the assets they already labeled, so the asset they are
    served has to be read this way.
    """
    return f"""
    query asset($id: ID!) {{
      data: asset(id: $id) {{
        {fragment}
      }}
    }}
    """


def get_label_for_user_query(fragment: str) -> str:
    """Return the query reading the label the labeling interface opens an asset with."""
    return f"""
    query getLabelsOrPredictionsForUser($assetID: ID!, $userID: ID!) {{
      data: getLabelsOrPredictionsForUser(assetID: $assetID, userID: $userID) {{
        {fragment}
      }}
    }}
    """


def get_label_to_review_query(fragment: str) -> str:
    """Return the query reading the label the review interface opens an asset with."""
    return f"""
    query getLabelsToBeReviewed($assetID: ID!) {{
      data: getLabelsToBeReviewed(assetID: $assetID, excludeAutosave: true) {{
        {fragment}
      }}
    }}
    """
