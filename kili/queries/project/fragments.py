PROJECT_FRAGMENT = '''
id
title
consensusTotCoverage
maxWorkerCount
minAgreement
minConsensusSize
interfaceCategory
inputType
consensusMark
honeypotMark
jsonInterface
numberOfRemainingAssets
numberOfAssets
numberOfAssetsWithSkippedLabels
numberOfReviewedAssets
numberOfLatestLabels
numberOfRoles
roles {
  id
  user { id, name, email }
  role
  consensusMark
  honeypotMark
  lastLabelingAt
  numberOfAnnotations
  numberOfLabels
  numberOfLabeledAssets
  totalDuration
}
'''
